import asyncio
from aiohttp import web
import subprocess
import shlex
import signal
import traceback
import os.path
import sys
import ssl
sys.path.append(os.path.dirname(__file__))
import config
import logging
import threading
import time

connectedUsers = []
availablePortMin = 49152
availablePortMax = 65535

def collectGarbage():
    global connectedUsers
    while True:
        time.sleep(config.GC_INTERVAL)
        for r in connectedUsers:
            # kill idle or zombie process
            if r[1].poll() is None and time.time() - r[2] > config.PROCESS_TIMEOUT:
                r[1].kill();
                #res = subprocess.check_call(shlex.split(f'kill -9 {pid}'))
                print(f'manager.collectGarbage > killed user process {r[1].pid}')
                connectedUsers.remove(r)
            # terminated process
            try:
                # check existence of a process by kill -0
                res = subprocess.check_call(shlex.split(f'kill -0 {r[1].pid}'))
            except subprocess.CalledProcessError as e:
                print(f'manager.collectGarbage > reclaimed port of dead process {r[1]}')
                # no process with the pid
                connectedUsers.remove(r)
            # defunct zombie??? https://ameblo.jp/yukozutakeshizu/entry-12526774342.html

def decide_userProperPorts():
    for i in range(availablePortMin, availablePortMax):
        if i in [p[0] for p in connectedUsers]:
            continue
        else:
            return i

def generate_startPage(userPort):
    page = ''
    with open('./www/start.html', 'r') as f:
        for line in f:
            if line.find('<title>') != -1:
                page += line + "\n"
                #page += f"<link rel = 'stylesheet' href='{config.PROTOCOL}://{config.HOST}:{config.HOST_PORT}/www/style.css' >\n"
                #page += f"<link rel='stylesheet' href='/www/style.css' >\n"
                page += f"<link rel='icon' type='image/png' href='/www/image/favicon.png' >\n"
            elif line.find('<img>') != -1:
                #page += f"<img src='{config.PROTOCOL}://{config.HOST}:{config.HOST_PORT}/www/image/logo.png' style='display:block; margin:auto;'>\n"
                page += f"<img src='/www/image/logo_xxxhdpi_192x192_rounded.png' style='display:block; margin:auto;'>\n"
            elif line.find('</body>') != -1:
                page += line + "\n"
                page += '<script>\n'
                #page += f"const WSURL = '{config.WS_PROTOCOL}://{config.HOST}:{userPort}/ws';\n"
                page += f"const WSURL = '{config.WS_PROTOCOL}://{config.HOST_EXTERNAL_IP}:{userPort}/ws';\n"
                page += f"const HOST = '{config.HOST_EXTERNAL_IP}';\n"
                page += f"const HOST_PORT = '{config.HOST_PORT}';\n"
                #page += f"const MIKE_ON_ICON = '{config.PROTOCOL}://{config.HOST}:{config.HOST_PORT}/www/image/mike_on.png';\n"
                page += f"const MIKE_ON_ICON = '/www/image/mike_on.png';\n"
                #page += f"const MIKE_OFF_ICON = '{config.PROTOCOL}://{config.HOST}:{config.HOST_PORT}/www/image/mike_off.png';\n"
                page += f"const MIKE_OFF_ICON = '/www/image/mike_off.png';\n"
                page += '</script>\n'
                #page += f"<script type='text/javascript' src='{config.PROTOCOL}://{config.HOST}:{config.HOST_PORT}/www/script.js' async></script>\n"
                page += f"<script type='text/javascript' src='/www/script.js' async></script>\n"
                #page += f"<script type='text/javascript' src='{config.PROTOCOL}://{config.HOST}:{config.HOST_PORT}/www/qrcodejs/qrcode.min.js' async></script>\n"
                #page += f"<script type='text/javascript' src='/www/qrcodejs/qrcode.min.js' async></script>\n"
            else:
                page += line
    return page

async def http_handler(request):
    print('manager.http_handler...')
    if 'file' in request.match_info:
        page = request.match_info['file']
        #if page == 'style.css':
        #    with open('./www/style.css', 'r') as f: page = f.read()
        #    print("manager.http_handler -> client > style.css")
        #    return web.Response(content_type='text/css', text=page)
        #el
        if page == 'script.js':
            with open('./www/script.js', 'r') as f: page = f.read()
            print("manager.http_handler -> client > script.js")
            return web.Response(content_type='text/javascript', text=page)
        elif page == 'service-worker.js':
            with open('./www/service-worker.js', 'r') as f: page = f.read()
            print("manager.http_handler -> client > service-worker.js")
            return web.Response(content_type='text/javascript', text=page)
        elif page == 'manifest.json':
            with open('./www/manifest.json', 'r') as f: page = f.read()
            print("manager.http_handler -> client > manifest.json")
            return web.Response(content_type='text/json', text=page)
        elif page == 'offline.html':
            with open('./www/offline.html', 'r') as f: page = f.read()
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
            userPort = decide_userProperPorts()
            start = time.time()
            userProc = subprocess.Popen(shlex.split(f'python3 ./user.py {userPort} {org} {role} {invoker}'))
            print(f'manager.websocket_handler > created a user proc {userProc.pid}')
            connectedUsers.append((userPort, userProc, start))
            page = generate_startPage(userPort);
            print(f"managee.http_handler -> client > index page")
            return web.Response(content_type='text/html', text=page)

async def on_shutdown(app):
    global connectedUsers
    print('user_manager.on_shutdown > clean up')
    await app.cleanup()
    for proc in [p[1] for p in connectedUsers]:
        proc.send_signal(signal.SIGINT)
    #await asyncio.sleep(5) # wait for profiler processing????
    for proc in [p[1] for p in connectedUsers]:
        pid = proc.pid
        res = subprocess.check_call(shlex.split(f'kill -9 {pid}'))
        print('killed user process {} -> {}'.format(pid, res))
        connectedUsers = []

def terminate(signum, frame):
    global connectedUsers
    try:
        for proc in [p[1] for p in connectedUsers]:
            pid = proc.pid
            res = subprocess.check_call(shlex.split('kill -9 {}'.format(pid)))
            print(f'manager.terminate > killed user process {pid} -> {res}')
            connectedUsers = []
    except subprocess.CalledProcessError as e:
        print(f'manager.terminate > cleanup return {e.returncode}, out {e.output}')

if __name__ == '__main__':
    print('manager starts')
    signal.signal(signal.SIGINT, terminate)
    signal.signal(signal.SIGTERM, terminate)
    try:

        #print("user_manager.main > start web server for static file requests")
        #proc = subprocess.Popen(shlex.split('python3 -m http.server'))

        if config.PROTOCOL=='http':
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
        #ctx.verify_mode = ssl.CERT_NONE

        logger = logging.getLogger('aiohttp.access')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        logger.addHandler(ch)

        print("manager.main > start dynamic web server: port", config.HOST_PORT)

        app = web.Application()
        #app.router.add_route('GET', '/www/{file}', http_handler)
        app.add_routes([
            #web.get('/www/', http_handler),
            web.get('/www/{file}', http_handler),
            web.static('/www/', './www/'),
        ])

        app.on_shutdown.append(on_shutdown)

        gc_flag = True
        th = threading.Thread(target=collectGarbage,
                              daemon=True) # kill thread when main ends
        th.start()

        if config.PROTOCOL=='http':
            web.run_app(app, host=config.HOST_INTERNAL_IP, port=config.HOST_PORT)
        else:
            web.run_app(app, host=config.HOST_INTERNAL_IP, port=config.HOST_PORT, ssl_context=ctx)

    except Exception as e:
        print(traceback.format_exc())
    finally:
        print("manager.main > clean up")
        terminate(None,None)



