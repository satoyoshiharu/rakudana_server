from aiohttp import web
import subprocess
import multiprocessing as mp
# import Process, Pipe
import shlex
import signal
import traceback
import ssl
import logging
import threading
import time
import MeCab
import sentencepiece as spm
from gensim.models import KeyedVectors
import torch
from intent_classifier import train
from intent_classifier import create_training_data
#import os.path, sys
#sys.path.append(os.path.dirname(__file__))
import user
import config
import com


def init_languagemodel():

    global tagger
    global tokenizer
    global wordvectors
    global intent_classifier

    print(f'init_LM > ...')

    tagger = MeCab.Tagger(r"-u ./user.dic -d /var/lib/mecab/dic/ipadic-utf8/")
    print(f'tagger type: {type(tagger)}')
    tagger.parse('私')  # preload dictionary

    tokenizer = spm.SentencePieceProcessor()
    tokenizer.Load("./tokenizer/sentencepiece.model")
    print(f'tokenizer loaded: {type(tokenizer)}')

    wordvectors = KeyedVectors.load('./intent_classifier/wv.model')
    print(f'word vector loaded: {type(wordvectors)}')

    szWV = 100
    numINTENT = com.INTENT_MAX + 1
    intent_classifier = train.Net(szWV, numINTENT)  # .to(device)
    intent_classifier.load_state_dict(torch.load('./intent_classifier/intent_classifier.model'))
    print(f'intent classifier loaded: {type(intent_classifier)}')


def lm(conn):

    global tagger
    global tokenizer
    global wordvectors
    global intent_classifier

    print('lm thread started')
    while True:
        req = conn.recv()
        print(f'lm < {req}')
        if req == 'finish$':
            break
        elif req[:4] == 'tag$':
            res = tagger.parse(req[4:])
            conn.send(res)
        elif req[:7] == 'intent$':
            input_data = torch.tensor(
                create_training_data.embAvg(req[7:], tokenizer, wordvectors),
                dtype=torch.float
            )
            intent_classifier.eval()
            with torch.no_grad():
                intent = torch.argmax(intent_classifier(torch.unsqueeze(input_data, 0))).item()
            print(f'detect_intent> {com.intents[intent]}')
            conn.send(str(intent))
    print('lm thread ended')


def collectGarbage():
    global connectedUsers
    while True:
        time.sleep(config.GC_INTERVAL)
        for r in connectedUsers:
            # kill idle or zombie process
            #if r[1].poll() is None and time.time() - r[2] > config.PROCESS_TIMEOUT:
            if r[1].is_alive() and time.time() - r[2] > config.PROCESS_TIMEOUT:
                r[1].kill()
                #res = subprocess.check_call(shlex.split(f'kill -9 {pid}'))
                print(f'manager.collectGarbage > killed user process {r[1].pid}')
                connectedUsers.remove(r)
            # terminated process
            try:
                # check existence of a process by kill -0
                subprocess.check_call(shlex.split(f'kill -0 {r[1].pid}'))
            except subprocess.CalledProcessError as e:
                print(f'No process {r[1].pid} in collectGarbage: {e}')
                # no process with the pid
                connectedUsers.remove(r)
            # defunct zombie??? https://ameblo.jp/yukozutakeshizu/entry-12526774342.html


def decide_userProperPorts():
    for i in range(availablePortMin, availablePortMax):
        if i in [p[0] for p in connectedUsers]:
            continue
        else:
            return i


def usedPort(port):
    if port in [p[0] for p in connectedUsers]:
        return True
    else:
        return False


def generate_startPage(userport):
    page = ''
    with open('./www/start.html', 'r') as f:
        for line in f:
            if line.find('<title>') != -1:
                page += line + "\n"
                page += f"<link rel='icon' type='image/png' href='/www/image/favicon.png' >\n"
            elif line.find('<img>') != -1:
                page += f"<img src='/www/image/logo_xxxhdpi_192x192_rounded.png' style='display:block; margin:auto;'>\n"
            elif line.find('</body>') != -1:
                page += line + "\n"
                page += '<script>\n'
                page += f"const WSURL = '{config.WS_PROTOCOL}://{config.HOST_EXTERNAL_IP}:{userport}/ws/b';\n"
                page += f"const HOST = '{config.HOST_EXTERNAL_IP}';\n"
                page += f"const HOST_PORT = '{config.HOST_PORT}';\n"
                page += f"const MIKE_ON_ICON = '/www/image/mike_on.png';\n"
                page += f"const MIKE_OFF_ICON = '/www/image/mike_off.png';\n"
                page += '</script>\n'
                page += f"<script type='text/javascript' src='/www/script.js' async></script>\n"
            else:
                page += line
    return page


async def http_handler(request):
    print('manager.http_handler...')
    if 'file' in request.match_info:
        page = request.match_info['file']
        # if page == 'style.css':
        #    with open('./www/style.css', 'r') as f: page = f.read()
        #    print("manager.http_handler -> client > style.css")
        #    return web.Response(content_type='text/css', text=page)
        # el
        if page == 'script.js':
            with open('./www/script.js', 'r') as f:
                page = f.read()
            print("manager.http_handler -> client > script.js")
            return web.Response(content_type='text/javascript', text=page)
        elif page == 'service-worker.js':
            with open('./www/service-worker.js', 'r') as f:
                page = f.read()
            print("manager.http_handler -> client > service-worker.js")
            return web.Response(content_type='text/javascript', text=page)
        elif page == 'manifest.json_string':
            with open('./www/manifest.json', 'r') as f:
                page = f.read()
            print("manager.http_handler -> client > manifest.json_string")
            return web.Response(content_type='text/json_string', text=page)
        elif page == 'offline.html':
            with open('./www/offline.html', 'r') as f:
                page = f.read()
            print("manager.http_handler -> client > offline.html")
            return web.Response(content_type='text/html', text=page)
        elif page == 'index.html':
            # page == 'index.html':
            #???print('cookie:', request.get_cookies['genkikai_id_3'])
            if 'invoker' in request.rel_url.query:
                invoker = request.rel_url.query['invoker']
                org = 'unknown'
                role = 'unknown'
            else:
                invoker = 'unknown'
                if 'org' in request.rel_url.query:
                    org = request.rel_url.query['org']
                else:
                    org = 'genkikai'
                if 'role' in request.rel_url.query:
                    role = request.rel_url.query['role']
                else:
                    role = 'member'
            if 'port' in request.rel_url.query:
                p = int(request.rel_url.query['port'])
                if usedPort(p):
                    return web.Response(content_type='text/html', text='failed')
                else:
                    user_port = p
            else:
                user_port = decide_userProperPorts()
            starttime = time.time()

            # userProc = subprocess.Popen(shlex.split(f'python3 ./user.py {userport} {org} {role} {invoker}'))
            # connectedUsers.append((userport, userProc, start))
            # mp.set_start_method('spawn')
            print(f'kick user process with port {user_port}')
            parent_conn, child_conn = mp.Pipe()
            userproc = mp.Process(target=user.main, args=(user_port, org, role, invoker, child_conn))
            userproc.start()

            print('kick lm thread')
            lmThread = threading.Thread(target=lm, args=[parent_conn], daemon=True)  # kill thread when main ends
            lmThread.start()

            connectedUsers.append((user_port, userproc, starttime, parent_conn, lmThread))

            print(f'manager.websocket_handler > created a user proc {userproc.pid} port {user_port}')

            page = generate_startPage(user_port)
            print(f"managee.http_handler -> client > index page")
            return web.Response(content_type='text/html', text=page)


async def on_shutdown(app):
    global connectedUsers
    print('user_manager.on_shutdown > clean up')
    await app.cleanup()
    for lmThread in [p[4] for p in connectedUsers]:
        lmThread.join()
    # for proc in [p[1] for p in connectedUsers]:
    #     proc.send_signal(signal.SIGINT)
    #await asyncio.sleep(5) # wait for profiler processing????
    for proc in [p[1] for p in connectedUsers]:
        pid = proc.pid
        res = subprocess.check_call(shlex.split(f'kill -9 {pid}'))
        print('killed user process {} -> {}'.format(pid, res))
        connectedUsers = []


def terminate(signum, frame):
    global connectedUsers
    try:
        for lmThread in [p[4] for p in connectedUsers]:
            lmThread.join()
        for proc in [p[1] for p in connectedUsers]:
            pid = proc.pid
            res = subprocess.check_call(shlex.split('kill -9 {}'.format(pid)))
            print(f'manager.terminate > killed user process {pid} -> {res}')
            connectedUsers = []
    except subprocess.CalledProcessError as e:
        print(f'manager.terminate > cleanup return {e.returncode}, out {e.output}')


connectedUsers = []
availablePortMin = 49152
availablePortMax = 65535
tagger = None
tokenizer = None
wordvectors = None
intent_classifier = None


if __name__ == '__main__':

    print('manager starts')
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)
    try:

        # print("user_manager.main > start web server for static file requests")
        # proc = subprocess.Popen(shlex.split('python3 -m http.server'))

        ctx = None
        if config.PROTOCOL == 'http':
            pass
        else:
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            if config.CLOUD_INSTANCE:
                ctx.load_cert_chain('/etc/letsencrypt/live/rakudana.com/fullchain.pem',
                                    keyfile='/etc/letsencrypt/live/rakudana.com/privkey.pem')
            else:
                ctx.load_cert_chain('server.crt', keyfile='server.key')
            # WebSockets require TLS 1.2 (TLS 1.3 is not supported)
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_3
            ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE

        logger = logging.getLogger('aiohttp.access')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        logger.addHandler(ch)

        init_languagemodel()

        mp.set_start_method('spawn')

        print("manager.main > start dynamic web server: port", config.HOST_PORT)

        manager = web.Application()
        # manager.router.add_route('GET', '/www/{file}', http_handler)
        manager.add_routes([
            # web.get('/www/', http_handler),
            web.get('/www/{file}', http_handler),
            web.static('/www/', './www/'),
        ])

        manager.on_shutdown.append(on_shutdown)

        gc_flag = True
        th = threading.Thread(target=collectGarbage, daemon=True)  # kill thread when main ends
        th.start()

        if config.PROTOCOL == 'http':
            web.run_app(manager, host=config.HOST_INTERNAL_IP, port=config.HOST_PORT)
        else:
            web.run_app(manager, host=config.HOST_INTERNAL_IP, port=config.HOST_PORT, ssl_context=ctx)

    except Exception as e:
        print(f'Exception in manager: {e}')
        print(traceback.format_exc())
    finally:
        print("manager.main > clean up")
        terminate(None, None)
