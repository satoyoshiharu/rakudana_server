"""
 UI, Communication controller
 Process per user
"""
from aiohttp import web
import traceback
import signal
import sys
import config
import line_config
import ip_config
import json
import ssl
import urllib.request
import logging
from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage
from datetime import datetime
import asyncio
import threading
import re
import names
from ner import NER, Person, Day, Reservation, Visit, Digits
import urllib.parse
import com


class User:
    """
    user attributes
    """
    def __init__(self, port, org, role, invoker, pipe):
        self.wsPort = int(port)
        self.ws = None
        self.appws = None
        self.app_data = False
        #self.monitor_info = None
        self.org = org
        self.role = role
        self.invoker = invoker
        self.pipe = pipe
        self.person = None
        self.dialog_history = []
        self.device = ''
        self.capability_sr = False
        self.capability_ss = False
        self.screen_width = 0
        self.screen_height = 0
        self.cookie = ''
        if self.invoker == 'rakudana_app':
            self.ner = NER(self)
            self.app_conn_flag = False
            self.app_close_flag = False
            self.contacts = []
            self.callrecs = []

    def cookie2id(self):
        print(f'cookie2id > {self.cookie}')
        if self.cookie != '':
            userid = re.findall(r'genkikai_id=([^,]*)', self.cookie)
            print(f'cookie2id > {userid[0]}')
            return userid[0]
        else:
            return ''


async def app_handler(request):
    global user
    print('app_handler...')
    ws = web.WebSocketResponse(timeout=60, max_msg_size=256)
    await ws.prepare(request)
    user.appws = ws
    print('app_handler > Websocket connection ready')
    r = await ws.receive()
    print(f'app_handler > received: {r}')
    d = r.data
    print(f'app_handler > data: {d}')
    user.app_conn_flag = True

    rs = d.split("\n")
    contacts_str = rs[0]
    callrecs_str = rs[1]
    print(f'app_handler > contacts {contacts_str}. callrecs {callrecs_str}')

    if len(contacts_str) > 0 and contacts_str[0] == ",": contacts_str = contacts_str[1:]
    contacts = contacts_str.split(",") # returns [''] in '' case
    if len(contacts) > 0 and contacts != ['']:
        user.contacts = [[c.split(":")[0], c.split(":")[1]] for c in contacts]
    else:
        user.contacts = []
    print(f"[DIALOG] app_handler > contacts: {user.contacts}")
    if len(callrecs_str) > 0 and callrecs_str[0] == ",": callrecs_str = callrecs_str[1:]
    callrecs = callrecs_str.split(",")
    if len(callrecs) > 0 and callrecs != ['']:
        user.callrecs = [[c.split(":")[0], c.split(":")[1]] for c in callrecs]
    else:
        user.callrecs = []
    print(f"[DIALOG] app_handler > call recs: {user.callrecs}")

    while not user.app_close_flag:
        await asyncio.sleep(1)

    await ws.close()
    print('app_handler > ended')
    return


async def browser_handler(request):
    global user
    print('browser_handler > Websocket connection starting')
    ws = web.WebSocketResponse(timeout=60, max_msg_size=256)
    user.ws = ws
    await ws.prepare(request)
    print('browser_handler > Websocket connection ready')

    # r = await user.ws.receive()
    # json_dict = json_string.loads(r.data)
    sts, json_dict = await recv_json(ws)
    if sts == com.SUCCESS:
        print(f'browser_handler > received: {json_dict}')

        if 'device' in json_dict:
            user.device = json_dict['device']
        if 'capability_ss' in json_dict and json_dict['capability_ss'] == '1':
            user.capability_ss = True
        if 'capability_sr' in json_dict and json_dict['capability_sr'] == '1':
            user.capability_sr = True
        if 'screen_width' in json_dict:
            user.screen_width = int(json_dict['screen_width'])
        if 'screen_height' in json_dict:
            user.screen_height = int(json_dict['screen_height'])
        if 'cookie' in json_dict:
            user.cookie = json_dict['cookie']

        conversation = ConversationModel(user)
        await conversation.loop()

    print('browser_handler > Websocket connection closed')
    ws.force_close()
    #print(user.dialog_history)
    sys.exit(0)
    #return user.ws

# end of conversation. It follows in browser AppLink or location.replace(url).
# User operation may be needed, and don't clea up DOM by finish command.
SCENE_LEAVE = 0
# end of conversation. End of Scenes. Clean up DOM by finish command.
SCENE_TERMINATE = -1

class ConversationModel:

    def __init__(self, usr):
        self.user = usr

    async def loop(self):
        json_text = '{"feedback":"???????????????"}'
        await self.user.ws.send_str(json_text)

        if self.user.invoker=='rakudana_app':
            while not self.user.app_conn_flag:
                await asyncio.sleep(0.1)
        else:
            await asyncio.sleep(1)

        scene = Initial(self.user)
        self.user.dialog_history.append(scene)

        try:
            while True:
                print(f'[DIALOG] ConversationMolde.loop > scene: {scene.__class__.__name__} prompt')
                await scene.prompt()
                # NER detection and Intent detection are done in decode_response
                print(f'[DIALOG] ConversationMolde.loop > scene: {scene.__class__.__name__} interpret')
                scene = await scene.interpret()
                # (1) explicit termination (2) timeout error (idle >10 minutes)
                if scene is SCENE_TERMINATE:
                    print('ConversationMolde.loop > scene is Terminate')
                    #await asyncio.sleep(10000)
                    json_text = '{' + f'"action":"finish"' + '}'
                    if not self.user.ws.closed:
                        await self.user.ws.send_str(json_text)
                    self.user.pipe.send('finish$')
                    break
                elif scene is SCENE_LEAVE:
                    print('ConversationMolde.loop > scene is Terminate')
                    self.user.pipe.send('finish$')
                    break
                self.user.dialog_history.append(scene)

        except Exception as e:
            # maybe timeout error
            print(f'ConversationModel.loop > exception: {e}')
            print(traceback.format_exc())

        #json_text = '{' + '"action":"finish"' + '}'
        #if not self.user.ws.closed:
        #    await self.user.ws.send_str(json_text)
        self.user.app_close_flag = True
        return  # -> finish


def send_json_sync(url, data):
    print(f'send_json > {url}, {data}')
    headers = {'Content-Type': 'application/json_string'}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        print('respose: ', res)
        json_contents = json.load(res)
        print('json_string contents', json_contents)


async def send_json(url, data):
    print(f'sendJson > {url}, {data}')
    headers = {'Content-Type': 'application/json_string'}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        print('respose: ', res)
        #try:
        json_contents = json.load(res)
        print('json_string contents', json_contents)
        return json_contents
        #except Exception as e:
        #    print(traceback.format_exc())
        #    return {}


def send_to_line(lineid, message):
    global line_bot_api
    #line_bot_api: LineBotApi
    if lineid is not None:
        line_bot_api.push_message(lineid, TextSendMessage(text=message))
        print(f'sent to {lineid}: {message}')
    else:
        line_bot_api.push_message(line_config.LINE_ADMIN_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(line_config.LINE_ADMIN2_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(line_config.LINE_ADMIN3_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(line_config.LINE_ADMIN4_USERID, TextSendMessage(text=message))


async def recv_json(ws):

    async def receive_json():
        try:
            while True:
                r = await ws.receive()
                print(f'[DIALOG] recv_json > received (raw): {r.data}')
                if type(r.data) is int:
                    print(f'recv_json > int returned {r.data}')
                    return com.ERR_TYPEERROR, None
                json_dict = json.loads(r.data)
                if len(r.data) == 0:
                    continue
                # print(f'recvJson > received(json_string): {jsondict}')
                if 'status' in json_dict:
                    continue
                else:
                    break
            return com.SUCCESS, json_dict
        # except json_string.decoder.JSONDecodeError:
        #     print('JsonDecode Exception in recvJson')
        #     print(traceback.format_exc())
        #     return {} #-> continue
        except TypeError:
            print('TypeError Exception in recv_json')
            print(traceback.format_exc())
            # ignore
            # await self.recvJson();
            return com.ERR_TYPEERROR, None  # -> continue
        except Exception as e:
            print(f'Exception in recv_json: {e}')
            print(traceback.format_exc())
            return com.ERR_EXCEPTION, None

    print('recv_json')
    try:
        sts, jsondict = await asyncio.wait_for(receive_json(), config.RECVJSON_TIMEOUT)
    except asyncio.TimeoutError:
        sts, jsondict = com.ERR_TIMEOUT, {}
        print(jsondict)
    return sts, jsondict


class Scene:

    def __init__(self, usr):
        self.user = usr
        self.ws = self.user.ws
        self.error = com.INF_OK
        self.counter = 0

    def get_morphs(self, jsondict):
        print('get_morphs > ...')
        v = jsondict['recognized']
        #parsed = self.tagger.parse(v)
        self.user.pipe.send('tag$' + v)
        parsed = self.user.pipe.recv()
        morphs = []
        for token in parsed.split('\n'):
            #attr = token.split('\t')
            attr = re.split('[\t,]', token)
            if DEBUG:
                print(f'get_morphs > attr: {attr}')
            # unidic-lite
            # morph = {'surface': attr[0], 'base': attr[4], 'pos': attr[4]}
            # IPA
            if len(attr) > 8:
                morph = {'surface': attr[0], 'pos': attr[1] + attr[2] + attr[3] + attr[4] + attr[5], 'base': attr[8]}
                morphs.append(morph)
            elif len(attr) > 1:
                morph = {'surface': attr[0], 'pos': attr[1] + attr[2] + attr[3] + attr[4] + attr[5]}
                morphs.append(morph)
            #else:
            #    morph = {'surface': attr[0]} # drop EOS, ''
            #morphs.append(morph)
        if DEBUG: print(f'morphs{morphs}')
        return morphs

    async def send_str(self, json_string):
        print(f'[DIALOG] send_str > {json_string}')
        try:
            if not self.ws.closed: await self.ws.send_str(json_string)
        except Exception as e:
            print('sending > exception {}'.format(e))
            print(traceback.format_exc())
            #print(f'{user.dialog_history}')
            exit(1)

    async def send_str_to_app_websocket(self, string):
        print(f'send_str_to_app_websocket > {string}')
        try:
            if not self.user.appws.closed:
                await self.user.appws.send_str(string)
        except Exception as e:
            print('sending > exception {}'.format(e))
            print(traceback.format_exc())

    async def prompt_and_interpret(self, scene):
        await scene.prompt()
        if scene.counter > 5:
            #await self.sendStr('{"feedback":"???????????????"}')
            scene.error = com.ERR_TIMEOUT
            return None
        scene.counter += 1
        return await scene.interpret()

    def detect_intent(self,text):
        print('detect_intent > ...')
        self.user.pipe.send('intent$' + text)
        return int(self.user.pipe.recv())

    async def decode_response(self):
        print('decode_response')

        sts, json_dict = await recv_json(self.ws)

        if sts != com.SUCCESS:
            print('decode_response > recv_json failed')
            return sts, None, None, None, None

        morphs = []
        selection = ''
        intent = -1
        if 'recognized' in json_dict:
            morphs = self.get_morphs(json_dict)
            print(f'[DIALOG] decode_response > morphs detected: {morphs}')

            if self.user.invoker == 'rakudana_app':
                # detect entities for following processing
                self.user.ner.find_entity(morphs)
                print(f'[DIALOG] decode_response > entity detected: {self.user.ner.entitylist}')
                # detect intention
                intent = self.detect_intent(json_dict['recognized'])
                print(f'[DIALOG] decode_response > intent detected: {com.intents[intent]}')

        if 'action' in json_dict and json_dict['action'] == 'button':
            selection = json_dict['selection']
            print(f'[DIALOG] decode_response > button action detected: {selection}')

        return sts, json_dict, morphs, selection, intent

    async def feedback(self, msg, pause):
        await self.send_str('{"feedback":"' + f'{msg}' + '"}')
        if pause > 0:
            await asyncio.sleep(pause)


class Initial(Scene):

    async def prompt(self):
        print('Initial.prompt')
        if self.error == com.INF_NO_TARGET_WORDS:
            speech = '???????????????'
            self.error = com.INF_RESET
        else:
            speech = '????????????????????????????????????'
        text = '???????????????'

        json_text = ''
        if self.user.invoker == 'rakudana_app':
            display = '<h3>????????????????????????????????????????????????????????????????????????????????????<br>?????????????????????????????????????????????</h3>'
            json_text = '{' + f'"speech":"{speech}","text":"{text}","show": "{display}",' +\
                        '"suggestions":["?????????","?????????","??????"]' + '}'
        elif self.user.org == 'genkikai':
            if self.user.role == 'admin':
                json_text = '{' + f'"speech":"{speech}","text":"{text}",' +\
                           '"suggestions":["????????????","????????????","??????"]' + '}'
            else:
                json_text = '{' + f'"speech":"{speech}","text":"{text}",' +\
                           '"suggestions":["????????????","????????????","????????????","??????","?????????"]' + '}'

        await self.send_str(json_text)
        return

    async def interpret(self):
        print('Initial.interpret')

        if self.counter > 3:
            await self.feedback("???????????????",1)
            return SCENE_TERMINATE

        sts, json_dict, morphs, selection, intent = await self.decode_response()

        if sts == com.ERR_TIMEOUT:
            await self.send_str('{"feedback":"???????????????????????????????????????"}')
            self.counter += 1
            await asyncio.sleep(1)
            return self

        if sts != com.SUCCESS:
            print('Initial.interpret > decode_response failed')
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        if self.user.invoker == 'rakudana_app':
            print('Initial.interpret > rakudana_app case')
            if intent == com.INTENT_HELP or selection == '1':
                await self.feedback("?????????????????????", 0)
                return RakudanaHelp(self.user, self)
            elif any(['??????' in m['surface'] for m in morphs]) or selection == '2':
                return GetFeedback(self.user, self)
            elif any(['??????' in m['surface'] for m in morphs]) or selection == '3':
                await self.feedback("???????????????", 0)
                return SeeYou(self.user)
            elif intent == com.INTENT_CHECK_SECURITY:
                await self.feedback("????????????????????????", 0)
                return await self.act_check_security()
            elif intent == com.INTENT_TEL:
                await self.feedback("???????????????", 0)
                return await self.act_make_call()
            elif intent == com.INTENT_CALL_POLICE:
                await self.feedback("????????????????????????", 0)
                return CallPoliceConfirm(self.user)
            elif intent == com.INTENT_CALL_EMERGENCY:
                await self.feedback("?????????????????????????????????", 0)
                return CallEmergencyConfirm(self.user)
            elif intent == com.INTENT_SEND_SHORT_MESSAGE:
                await self.feedback("??????????????????????????????????????????", 0)
                return SendShortMessageInput(self.user)
            elif intent == com.INTENT_SEND_LINE_MESSAGE:
                await self.feedback("LINE??????????????????????????????", 0)
                return SendLineMessageInput(self.user)
            elif intent == com.INTENT_SAVE_MEMO:
                await self.feedback("???????????????????????????", 0)
                return await self.act_save_memo()
            elif intent == com.INTENT_PUT_PAGE_SHORTCUT:
                await self.feedback("??????????????????????????????????????????", 0)
                return await self.act_put_page_shortcut()
            elif intent == com.INTENT_MAP:
                await self.feedback("?????????????????????", 0)
                return await self.act_open_map(json_dict['recognized'])
            elif intent == com.INTENT_NEWS:
                await self.feedback("?????????????????????", 0)
                return await self.act_open_news(json_dict, morphs)
            elif intent == com.INTENT_WEATHER:
                await self.feedback("???????????????", 0)
                return await self.act_open_weather()
            elif intent == com.INTENT_CALCULATOR:
                await self.feedback("???????????????", 0)
                return await self.act_open_calculator()

            elif intent == com.INTENT_GENKIKAI:
                await self.feedback("????????????????????????", 0)
                self.user.invoker = ''
                self.user.org = 'genkikai'
                self.user.role = 'member'
                return Initial(self.user)
            elif intent == com.INTENT_GENKIKAI_ADMIN:
                await self.feedback("???????????????????????????????????????", 0)
                self.user.invoker = ''
                self.user.org = 'genkikai'
                self.user.role = 'admin'
                return Initial(self.user)
            elif intent == com.INTENT_GENKIKAI_MYRESERVATION:
                await self.feedback("???????????????????????????????????????", 0)
                return await self.act_myreservation()
            elif intent == com.INTENT_GENKIKAI_NEWS:
                await self.feedback("?????????????????????????????????????????????", 0)
                return await self.act_genkikai_news()
            elif intent == com.INTENT_GENKIKAI_MANAGE_RECORDS:
                await self.feedback("???????????????????????????????????????", 0)
                return Reserve(self.user, None)
            elif intent == com.INTENT_GENKIKAI_MANAGE_RESERVATIONS:
                await self.feedback("???????????????????????????????????????", 0)
                return Record(self.user, None)

            elif intent == com.INTENT_OTHERS:
                return await self.act_others(json_dict)

            self.error = com.INF_NO_TARGET_WORDS
            await self.send_str('{"feedback":"???????????????????????????????????????"}')
            self.counter += 1
            await asyncio.sleep(1)
            return self

        elif self.user.org == 'genkikai':

            if self.user.role == 'admin':
                print('Initial.interpret > genkikai admin case')
                if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
                    await self.feedback("????????????????????????", 0)
                    return Reserve(self.user, None)
                if any(['??????' in m['surface'] for m in morphs]) or any(['??????' in m['surface'] for m in morphs]) \
                        or any(['??????' in m['surface'] for m in morphs]) or selection == '2':
                    await self.feedback("?????????????????????????????????", 0)
                    return Record(self.user, None)
                if any(['??????' in m['surface'] for m in morphs]) or selection == '3':
                    await self.feedback("???????????????", 0)
                    return SeeYou(self.user)

                self.error = com.INF_NO_TARGET_WORDS
                self.counter += 1
                await asyncio.sleep(1)
                return self

            else:
                print('Initial.interpret > genkikai member case')
                if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
                    await self.feedback("????????????????????????", 0)
                    return await self.act_myreservation()
                if any(['??????' in m['surface'] for m in morphs]) or selection == '2':
                    await self.feedback("????????????????????????????????????", 2)
                    return await self.act_genkikai_news()
                if any(['????????????' in m['surface'] for m in morphs]) or selection == '3':
                    await self.feedback("??????????????????????????????", 0)
                    return await self.act_mypoint()
                if any(['??????' in m['surface'] for m in morphs]) or selection == '4':
                    await self.feedback("???????????????", 0)
                    return SeeYou(self.user)
                if any(['???' in m['surface'] for m in morphs]) or selection == '5':
                    return Secondary(self.user, self)

                self.error = com.INF_NO_TARGET_WORDS
                await self.send_str('{"feedback":"???????????????????????????????????????"}')
                self.counter += 1
                await asyncio.sleep(1)
                return self

    async def act_check_security(self):
        print('act_check_security')
        url = 'https://npogenkikai.net/security-check-quize/'
        await self.send_str('{' + f'"action":"goto_url","url":"{url}"' + '}')
        return SCENE_LEAVE

    async def act_others(self, json_dict):
        print('act_others')
        question = f"???{json_dict['recognized']}????????????????????????????????????????????????????????????"
        await self.feedback(question, 2)

        query = urllib.parse.quote(json_dict['recognized'])
        url = 'https://www.google.co.jp/search'
        await self.send_str('{' + f'"action":"goto_url","url":"{url}?q={query}&oq={query}&hl=ja&ie=UTF-8"' + '}') # go directly
        # url = f'apps://rakudana.com/client_app/search?query={query}'
        # guide = '????????????????????????????????????'
        # json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"{guide}"' + '}'
        # print(f'act_make_call > json_text: {json_text} -> browser')
        # await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_make_call(self):

        def match(prsn, datalist):
            print(f'act_make_call.match > prsn {prsn} vs datalist {datalist}')
            telnum = '0'
            match = [d for d in datalist if d[0] == prsn.name]
            print(f'act_make_call.match > match {match}')
            if len(match) > 0 and match != []:
                telnum = match[0][1]
            return telnum

        def make_url_with_name():
            name = self.user.ner.entitylist[0].name
            print(f'act_make_call > name {name}')
            name = urllib.parse.quote(name)
            return f'apps://rakudana.com/client_app/make_call?contact={name}'

        async def invoke_client(url, guide):
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"{guide}"' + '}'
            print(f'act_make_call > json_text: {json_text} -> browser')
            await self.send_str(json_text)

        print('act_make_call')

        if len(self.user.ner.entitylist) > 0:

            persons = [p for p in self.user.ner.entitylist if isinstance(p, Person)]
            print(f'act_make_call > persons:{persons}')
            digits = [d for d in self.user.ner.entitylist if isinstance(d, Digits)]
            print(f'act_make_call > digits:{digits}')
            if len(persons) > 0:
                person = persons[0]
                print(f'act_make_call > prsn {person.name} named')

                if len(self.user.contacts) > 0:
                    telnum = match(person, self.user.contacts)
                    if telnum != '0':
                        print(f'act_make_call > prsn matched with one of registered contacts {telnum}')
                        return MakeCallToConfirm(self.user, person, telnum)

                print(f'act_make_call > no match with contacts')
                if len(self.user.callrecs) > 0:
                    telnum = match(person, self.user.callrecs)
                    if telnum != '0':
                        print(f'act_make_call > prsn matched with one of call records {telnum}')
                        # ask confirmation to directly dial it, and show option to create shortcut button.
                        return MakeCallToARecord(self.user, person, telnum)

                print(f'act_make_call > prsn named but neither matched with registered contacts nor records')
                # fall-through to initial treatment : return MakeCallToContacts(self.user)
                await invoke_client(make_url_with_name(),
                                    "????????????????????????????????????????????????????????????????????????")
                return SCENE_LEAVE

            elif len(digits) > 0:
                digit = digits[0].value
                print(f'act_make_call > digits {digit} voiced')
                return MakeCallToNumberConfirm(self.user, digit)

            # initially just pass personal name to client
            # print(f'act_make_call > match with neither registered contact nor call records')
            # name = self.user.ner.entitylist[0].sei + self.user.ner.entitylist[0].mei
            # print(f'act_make_call > name {name}')
            # name = urllib.parse.quote(name)
            # url = f'apps://rakudana.com/client_app/make_call?contact={name}'
            await invoke_client(make_url_with_name(),
                                "????????????????????????????????????????????????????????????????????????")
            return SCENE_LEAVE

        else:
            print(f'act_make_call > neither name nor number prsn voiced')
            if len(self.user.contacts) > 0:
                return MakeCallToContacts(self.user)
            else:
                await invoke_client('apps://rakudana.com/client_app/make_call',
                                    "????????????????????????????????????????????????????????????????????????")
                return SCENE_LEAVE

        # json_text = '{' + f'"action":"invoke_app","url":"{url}"' + '}'
        # print(f'act_make_call > json_text: {json_text} -> browser')
        # await self.send_str(json_text)
        #await invoke_client(url)
        #return SCENE_LEAVE

    async def act_save_memo(self):
        print('act_save_memo')
        await self.feedback("????????????????????????????????????????????????????????????????????????", 2)
        url = f'apps://rakudana.com/client_app/save_memo'
        guide = '????????????????????????????????????????????????????????????????????????'
        json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"{guide}"' + '}'
        print(f'act_make_call > json_text: {json_text} -> browser')
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_put_page_shortcut(self):
        print('act_save_memo')
        await self.feedback("?????????????????????????????????????????????QR?????????????????????????????????", 2)
        url = f'apps://rakudana.com/client_app/put_page_shortcut'
        guide = '????????????QR?????????????????????????????????'
        json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"{guide}"' + '}'
        print(f'act_make_call > json_text: {json_text} -> browser')
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_open_map(self, query):
        print('act_open_map')
        # invoke Android google map app.
        # https://www.google.co.jp/map/?hl=ja will not provide mike option
        # In addition, let android analyze from/to parsing
        await self.feedback("??????????????????????????????????????????", 0)
        url = f'apps://rakudana.com/client_app/map'
        q = urllib.parse.quote(query)
        json_text = '{' + f'"action":"invoke_app","url":"{url}?q={q}"' + '}'
        print(f'act_make_call > json_text: {json_text} -> browser')
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_open_news(self, json_dict, morphs):
        print('act_open_news')
        surface = [m['surface'] for m in morphs]
        i = surface.index('????????????')
        if i > 1 and (surface[i-1] == '???' or surface[i-1] == '????????????'):
            await self.feedback("?????????????????????????????????", 1)
            query = urllib.parse.quote(json_dict['recognized'])
            url = 'https://www.google.co.jp/search'
            await self.send_str(
                '{' + f'"action":"goto_url","url":"{url}?q={query}&oq={query}&hl=ja&ie=UTF-8"' + '}')  # go directly
        else:
            await self.feedback("????????????????????????????????????????????????",1)
            url = 'https://news.yahoo.co.jp/'
            await self.send_str('{' + f'"action":"goto_url","url":"{url}"' + '}') # go directly
        return SCENE_LEAVE

    async def act_open_weather(self):
        print('act_open_weather')
        # direct to hhttps://www.weathernews.jp
        await self.feedback("??????????????????????????????????????????????????????", 0)
        url = 'https://www.weathernews.jp/'
        json_text = '{' + f'"action":"goto_url","url":"{url}"' + '}'
        print(f'act_make_call > json_text: {json_text} -> browser')
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_open_calculator(self):
        print('act_open_calculator')
        # direct to hhttps://www.weathernews.jp
        await self.feedback("?????????????????????????????????", 0)
        url = f'https://www.webdentaku.com/'
        json_text = '{' + f'"action":"goto_url","url":"{url}"' + '}'
        print(f'act_make_call > json_text: {json_text} -> browser')
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def id2person(self, userid):
        print(f'id2person>{userid}')
        if userid == '':
            return None
        json_contents = \
            json.loads(names.nametable[(names.nametable['id'] == userid)]
                       .to_json(orient="records", force_ascii=False))
        print(f'id2person > cache returns {json_contents}')
        if len(json_contents) > 0:
            print(f'id2person > hit cache {json_contents}')
            json_contents = json_contents[0]
        else:
            json_contents = await send_json("https://npogenkikai.net/id2name.php", {"id": userid})
            print(f'id2person > id2name returns {json_contents}')
        person = Person(json_contents['sei'], json_contents['seiyomi'],
                        json_contents['mei'], json_contents['meiyomi'],
                        userid, json_contents['lineid'])
        await self.feedback(f'{person.seiyomi}{person.meiyomi}???????????????', 0)
        return person

    async def act_myreservation(self):
        print('act_myreservation')
        userid = self.user.cookie2id()
        if userid != '':
            self.user.person = await self.id2person(userid)
        else:
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
                if len(persons) == 1:
                    self.user.person = persons[0]
        #await self.feedback("???????????????????????????????????????",2)
        url = 'https://npogenkikai.net/reservations?id=' + self.user.person.id
        json_text = '{' + f'"action":"goto_url","url":"{url}"' + '}'
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_mycode(self):
        print('act_mycode')
        userid = self.user.cookie2id()
        if userid != '':
            self.user.person = await self.id2person(userid)
        else:
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
                if len(persons) == 1: self.user.person = persons[0]
        #return ShowMyCode(self.user)
        #await self.feedback("????????????????????????????????????",2)
        url = 'https://npogenkikai.net/myqrcode?id=' + self.user.person.id
        await self.send_str('{' + f'"action":"goto_url","url":"{url}"' + '}')
        return SCENE_LEAVE

    async def act_genkikai_news(self):
        print('act_news')
        url = 'https://npogenkikai.net/news'
        await self.send_str('{' + f'"action":"goto_url","url":"{url}"' + '}')
        return SCENE_LEAVE
        #return ViewInlineFrame(self.user, URL)

    async def act_mypoint(self):
        print('actMyPoint.react')
        userid = self.user.cookie2id()
        if userid != '':
            self.user.person = await self.id2person(userid)
        else:
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
                if len(persons) == 1:
                    self.user.person = persons[0]

        url = 'https://npogenkikai.net/mypoints2?id=' + self.user.person.id
        json_text = '{' + f'"action":"goto_url","url":"{url}"' + '}'
        await self.send_str(json_text)
        return SCENE_LEAVE
        #return ViewInlineFrame(self.user, url)


class RakudanaHelp(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.user = usr
        self.parent = parent

    async def prompt(self):
        print('RakudanaHelp.prompt')
        text = '???????????????????????????????????????????????????????????????'
        speech = '??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????'
        display = '<br>???????????????????????????????????????????????????????????????????????????????????????????????????' +\
                    '?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????' +\
                    '????????????????????????????????????????????????????????????????????????????????????????????????????????????NPO??????????????????????????????????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show": "{display}"' +\
                    ',"suggestions":["??????","??????"]'+ '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('RakudanaHelp.interpret')
        if self.counter > 5:
            await self.feedback("???????????????",1)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("????????????????????????????????????????????????", 2)
            url = 'https://rakudana.com:8080/www/doc/index.html'
            await self.send_str('{' + f'"action":"goto_url","url":"{url}"' + '}')
            return SCENE_LEAVE
        elif any([m['surface'].startswith('???') for m in morphs]) or selection == '2':
            await self.feedback("???????????????", 0)
            return self.parent
        else:
            self.error = com.INF_NO_TARGET_WORDS
            self.counter += 1
            await asyncio.sleep(1)
            return self


class GetFeedback(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.user = usr
        self.parent = parent

    async def prompt(self):
        print('GetFeedback.prompt')
        text = '?????????????????????????????????????????????????????????'
        speech = '?????????????????????????????????????????????????????????'
        display = ''
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show": "{display}"' +\
                    ',"suggestions":["???????????????"]'+ '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('GetFeedback.interpret')
        if self.counter > 5:
            await self.feedback("???????????????",1)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if len(morphs) > 0:
            return ConfirmFeedback(self.user,self,json_dict["recognized"])
        elif intent == com.INTENT_CANCEL or selection == '1':
            return self.parent
        else:
            self.error = com.INF_NO_TARGET_WORDS
            self.counter += 1
            await asyncio.sleep(1)
            return self


class ConfirmFeedback(Scene):

    def __init__(self, usr, parent, feedback):
        super().__init__(usr)
        self.user = usr
        self.parent = parent
        self.feedbackComment = feedback

    async def prompt(self):
        print('ConfirmFeedback.prompt')
        text = '????????????????????????????????????????????????'
        speech = '????????????????????????????????????????????????'
        display = self.feedbackComment
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show": "{display}"' + \
                    ',"suggestions":["??????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('ConfirmFeedback.interpret')
        if self.counter > 5:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("??????????????????????????????????????????????????????????????????????????????", 0)
            print(f'FEEDBACK: {self.feedbackComment}')
            return Initial(self.user)
        elif intent == com.INTENT_CANCEL or selection == '1':
            return self.parent
        else:
            self.error = com.INF_NO_TARGET_WORDS
            self.counter += 1
            await asyncio.sleep(1)
            return self


class Secondary(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.user = usr
        self.parent = parent

    async def prompt(self):
        print('Secondary.prompt')
        speech = '??????????????????????????????????????????????????????????????????ID?????????????????????????????????' +\
                 '??????ID?????????????????????????????????????????????????????????????????????'
        if self.user.device == 'iPhone':
            speech += '?????????????????????Safari???????????????????????????????????????????????????????????????ON??????????????????????????????????????????'
        text = '????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["????????????","??????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('Secondary.interpret')
        if self.counter > 5:
            await self.feedback("???????????????",1)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("??????????????????", 0)
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
                if persons != [] and len(persons) == 1:
                    self.user.person = persons[0]
            # store ID in client browser as Cookie
            # max-age is 60 days->5184000
            cookie = f'genkikai_id={self.user.person.id}; host={config.HOST_EXTERNAL_IP}; ' +\
                     'path=/; max-age=5184000; secure; SameSite=Strict;'
            json_text = '{' + f'"action":"set_cookie","cookie":"{cookie}"' + '}'
            await self.send_str(json_text)
            await self.feedback("????????????ID????????????????????????", 2)
            self.user.cookie = f'genkikai_id={self.user.person.id}'
            return self.parent
        elif any([m['surface'].startswith('???') for m in morphs]) or selection == '2':
            await self.feedback("???????????????", 0)
            return self.parent
        else:
            self.error = com.INF_NO_TARGET_WORDS
            self.counter += 1
            await asyncio.sleep(1)
            return self


class CallPoliceConfirm(Scene):

    async def prompt(self):
        # ask confirmation to directly dial it, and show option to create shortcut button.
        print('CallPoliceConfirm.prompt')
        speech = '110?????????????????????'
        text = '110?????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["??????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('CallPoliceConfirm.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            # url = 'tel://110'
            url = 'tel://09029355792' # for test
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"?????????????????????100?????????????????????"' + '}'
            print(f'CallPoliceConfirm > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif intent == com.INTENT_CANCEL or selection == '2':
            return SCENE_TERMINATE


class CallEmergencyConfirm(Scene):

    async def prompt(self):
        # ask confirmation to directly dial it, and show option to create shortcut button.
        print('CallEmergency.prompt')
        speech = '119?????????????????????'
        text = '119?????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["??????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('CallEmergencyConfirm.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            # url = 'tel://119'
            url = 'tel://09029355792' # for test
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"?????????????????????119????????????????????????"' + '}'
            print(f'CallPoliceConfirm > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif intent == com.INTENT_CANCEL or selection == '2':
            return SCENE_TERMINATE


class MakeCallToConfirm(Scene):

    def __init__(self, usr, person, number):
        super().__init__(usr)
        self.callto_name = person.name
        self.callto_number = number

    async def prompt(self):
        # ask confirmation to directly dial it, and show option to create shortcut button.
        print('MakeCallToConfirm.prompt')
        speech = f'{self.callto_name}??????????????????????????????'
        text = f'{self.callto_name}???????????????{self.callto_number}'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["??????","?????????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('MakeCallTo.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            url = f'tel://{self.callto_number}'
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"???????????????????????????????????????"' + '}'
            print(f'MakeCallTo > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif any(['???' in m['surface'] for m in morphs]) or selection == '2':
            name = self.callto_name
            url = f'apps://rakudana.com/client_app/make_call?contact={name}'
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"???????????????????????????????????????????????????"' + '}'
            print(f'MakeCallTo > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif intent == com.INTENT_CANCEL or selection == '3':
            return SCENE_TERMINATE


class MakeCallToNumberConfirm(Scene):

    def __init__(self, usr, number):
        super().__init__(usr)
        self.callto_number = number

    async def prompt(self):
        # ask confirmation to directly dial it, and show option to create shortcut button.
        print('MakeCallToNumberConfirm.prompt')
        speech = f'{self.callto_number}??????????????????????????????'
        text = f'{self.callto_number}???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["??????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('MakeCallToNumberConfirm.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            url = f'tel://{self.callto_number}'
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"?????????????????????{self.callto_number}??????????????????"' + '}'
            print(f'MakeCallTo > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif intent == com.INTENT_CANCEL or selection == '2':
            return SCENE_TERMINATE


class MakeCallToARecord(Scene):

    def __init__(self, usr, person, number):
        super().__init__(usr)
        self.callto_name = person.name
        self.callto_number = number

    async def prompt(self):
        # ask confirmation to directly dial it, and show option to create shortcut button.
        print('MakeCallTo.prompt')
        speech = f'{self.callto_name}????????????{self.callto_number}?????????????????????????????? ??????????????????????????????????????????'
        text = f'{self.callto_name}???????????????{self.callto_number}'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["??????","?????????","??????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('MakeCallToARecord.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            url = f'tel://{self.callto_number}'
            json_text = \
                '{' \
                + f'"action":"invoke_app","url":"{url}",' \
                  f'"guide":"??????????????????????????????{self.callto_name}?????????????????????"' \
                + '}'
            print(f'MakeCallTo > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif any(['???' in m['surface'] for m in morphs]) or selection == '2':
            name = self.callto_name
            url = f'apps://rakudana.com/client_app/make_call?contact={name}'
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"???????????????????????????????????????????????????"' + '}'
            print(f'MakeCallTo > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '3':
            # record the contact
            self.user.contacts.append([self.callto_name,self.callto_number])
            await self.send_str_to_app_websocket(
                ','.join([c[0] + ':' + c[1] for c in self.user.contacts])
            )
            # show contact buttons
            return MakeCallToContacts(self.user)
        elif intent == com.INTENT_CANCEL or selection == '4':
            return SCENE_TERMINATE


class MakeCallToContacts(Scene):

    async def prompt(self):
        # show contact list to push.
        print('MakeCallToContacts.prompt')
        speech = f'?????????????????????????????????????????????????????????????????????'
        text = f'?????????????????????????????????????????????'

        #send contact list. Browser will draw their buttons
        contacts = ','.join([c[0] + ':' + c[1] for c in self.user.contacts])

        suggestions = '["?????????","???????????????","???????????????"]'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","contacts":"{contacts}","suggestions":{suggestions}' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('MakeCallToContacts.interpret')
        # contact buttons -> tel directly in browser, not return here
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        elif any(['???' in m['surface'] for m in morphs]) or selection == '1':
            url = f'apps://rakudana.com/client_app/make_call'
            json_text = '{' + f'"action":"invoke_app","url":"{url}","guide":"???????????????????????????????????????????????????"' + '}'
            print(f'MakeCallTo > json_text: {json_text} -> browser')
            await self.send_str(json_text)
            return SCENE_LEAVE
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '2':
            print(f'MakeCallToContacts.interpret > delete selected')
            return DeleteContact(self.user, self)
        elif intent == com.INTENT_CANCEL or selection == '3':
            return SCENE_TERMINATE


class DeleteContact(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent

    async def prompt(self):
        # show contact list to push.
        print('DeleteContact.prompt')
        speech = f'??????????????????????????????????????????'
        text = f'??????????????????????????????????????????'

        #send contact list. Browser will draw their buttons
        contacts = ','.join([c[0] + ':' + c[1] for c in self.user.contacts])
        json_text = '{' + f'"speech":"{speech}", "text":"{text}", "delete":"{contacts}", "suggestions":["???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('DeleteContact.interpret')
        # contact buttons invoke tel directly in browser, not return here
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        elif intent == com.INTENT_CANCEL or selection == '0':
            print(f'EditContacts.interpret > finish selected')
            return MakeCallToContacts(self.user)
        elif selection != "" and selection != '0':
            self.user.contacts.pop(int(selection) - 1)
            await self.send_str_to_app_websocket(
                ','.join([c[0] + ':' + c[1] for c in self.user.contacts])
            )
            return MakeCallToContacts(self.user)


class SendShortMessageInput(Scene):

    async def prompt(self):
        print('SendShortMessageInput.prompt')
        speech = '????????????????????????????????????????????????'
        text = '??????????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('SendShortMessageInput.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if len(morphs) > 0:
            print(f"SendShortMessageInput.interpret > {json_dict['recognized']}")
            return SendShortMessageConfirm(self.user, self, json_dict['recognized'])
        else:
            return self


class SendShortMessageConfirm(Scene):

    def __init__(self, usr, parent, msg):
        super().__init__(usr)
        self.user = usr
        self.msg = msg
        self.parent = parent

    async def prompt(self):
        print('SendShortMessageConfirm.prompt')
        speech = '????????????????????????????????????????????????'
        text = 'OK???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show":"{self.msg}",' +\
                    '"suggestions":["??????","????????????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('SendShortMessage.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS or intent == com.INTENT_CANCEL or selection == '3':
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        elif intent == com.INTENT_RETRY or selection == '2':
            return self.parent
        elif intent == com.INTENT_YES or selection == '1':
            msg = urllib.parse.quote(self.msg)
            url = f'apps://rakudana.com/client_app/send_short_message?text={msg}'
            json_text = '{' + f'"action":"invoke_app","url":"{url}"' + '}'
            print(json_text)
            await self.send_str(json_text)
            return SCENE_LEAVE


class SendLineMessageInput(Scene):

    async def prompt(self):
        print('SendLineMessageInput.prompt')
        speech = '????????????????????????????????????????????????'
        text = '??????????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('SendLineMessageInput.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if len(morphs) > 0:
            return SendLineMessageConfirm(self.user, self, json_dict['recognized'])
        else:
            return self


class SendLineMessageConfirm(Scene):

    def __init__(self, usr, parent, msg):
        super().__init__(usr)
        self.user = usr
        self.msg = msg
        self.parent = parent

    async def prompt(self):
        print('SendLineMessageConfirm.prompt')
        speech = '????????????????????????????????????????????????'
        text = 'OK???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show":"{self.msg}",' +\
                    '"suggestions":["??????","????????????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('SendLineMessage.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS or intent == com.INTENT_CANCEL or selection == '3':
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        elif intent == com.INTENT_RETRY or selection == '2':
            return self.parent
        elif intent == com.INTENT_YES or selection == '1':
            msg = urllib.parse.quote(self.msg)
            url = f'https://line.me/R/share?text={msg}'
            json_text = '{' + f'"action":"invoke_app","url":"{url}"' + '}'
            print(json_text)
            await self.send_str(json_text)
            return SCENE_LEAVE


class AskName(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent

    async def prompt(self):
        print('AskName.prompt')
        if self.error == com.INF_NO_MATCHING_NAME:
            speech = '???????????????????????????????????????????????????????????????????????????????????????????????????'
            self.error = com.INF_RESET
        elif self.error == com.INF_NOT_HEAR_WELL:
            speech = '???????????????????????????????????????'
            self.error = com.INF_RESET
        elif self.error == com.INF_NO_TARGET_WORDS:
            speech = '????????????????????????????????????'
        else:
            speech = '???????????????????????????'
        text = '???????????????????????????'
        if self.user.org == 'genkikai' and self.user.role == 'member' and self.user.device == 'iPhone':
            # not self.user.capability_sr):
            json_text = '{' + f'"speech":"{speech}","text":"{text}"' + \
                ',"suggestions":["??????","?????????","??????","?????????","??????","???","??????","??????","??????","?????????","?????????"]' + '}'
        else:
            json_text = '{' + f'"speech":"{speech}","text":"{text}"' + '}'
        await self.send_str(json_text)
        return

    def parse_seimei(self, morph1, morph2):
        print(f'parse_seimei > {morph1}, {morph2}')
        if len(morph1) > 1 and 'pos' in morph1.keys() and morph1['pos'] == '???????????????????????????*' and\
                'pos' in morph2.keys() and morph2['pos'] == '???????????????????????????*':
            print(f'parse_seimei > found sei mei candidate')
            return morph1['surface'], morph1['base'], morph2['surface'], morph2['base']
        else:
            return '', '', '', ''

    def parse_mei(self, morph):
        print(f'parse_mei > {morph}')
        if 'pos' in morph.keys() and (morph['pos'] == '???????????????????????????*' or morph['pos'].startswith('??????????????????')):
            print(f'parse_mei > found sei candidate')
            if 'base' in morph:
                return morph['surface'], morph['base']
            else:
                return '', ''
        else:
            return '', ''

    async def parse_name(self, morphs):
        print(f'parse_name > {morphs}')
        json_contents = ''
        personlist = []
        idx = 0
        while True:
            if idx == len(morphs): break
            sei, seiyomi, mei, meiyomi = '', '', '', ''
            if idx + 1 <= len(morphs) - 1:
                sei, seiyomi, mei, meiyomi = self.parse_seimei(morphs[idx], morphs[idx + 1])
            if seiyomi != '' and meiyomi != '':
                # try nametable cache first
                json_contents = \
                    json.loads(names.nametable[
                                   (names.nametable['seiyomi'] == seiyomi) & (names.nametable['meiyomi'] == meiyomi)
                    ].to_json(orient="records", force_ascii=False))
                print(f'parse_name > cache returns {json_contents}')
                if len(json_contents) > 0:
                    print(f'parse_name > yomi hit cache {json_contents}')
                else:
                    #????????????->SR returns ?????????', base'??????????????? -> here try to match base form'????????????' against DB.
                    # Mostly it works to register surface form which SR recognized as user word of Mecab.
                    json_contents = await send_json(
                        "https://npogenkikai.net/name2id.php",
                        {"seiyomi": seiyomi, "meiyomi": meiyomi}
                    )
                    print(f'parse_name > with yomi, name2id returns {json_contents}')
                    # try to match ????????????
                    if len(json_contents) == 0:
                        json_contents = await send_json(
                            "https://npogenkikai.net/name2id.php",
                            {"sei": sei, "meiyomi": meiyomi}
                        )
                        print(f'parse_name > with hyouki, name2id returns {json_contents}')
                idx += 1
            else:
                # try with sei only
                sei, seiyomi = self.parse_mei(morphs[idx])
                if seiyomi != '':
                    json_contents = json.loads(
                        names.nametable[names.nametable['seiyomi'] == seiyomi]
                        .to_json(orient="records", force_ascii=False)
                    )
                    if len(json_contents) > 0:
                        print(f'parse_name > cache returns {json_contents}')
                    else:
                        json_contents = await send_json(
                            "https://npogenkikai.net/name2id.php",
                            {"seiyomi": seiyomi}
                        )
                        print(f'parse_name > name2id returns {json_contents}')
            if seiyomi != '':
                if json_contents == [] or json_contents == '' or 'error' in json_contents:
                    if meiyomi != '':
                        await self.feedback(seiyomi + meiyomi + '????????????????????????????????????????????????', 0)
                    else:
                        await self.feedback(seiyomi + '????????????????????????????????????????????????', 0)
                    self.error = com.INF_NO_MATCHING_NAME
                    return []
                elif len(json_contents) > 1:
                    multiple_mei = ' '.join([c['meiyomi']+'??????' for c in json_contents])
                    await self.feedback(seiyomi + '?????????????????????????????????????????????' +
                                        multiple_mei + '???????????????????????????????????????', 0)
                    self.error = com.INF_MULTIPLE_MATCH
                    return []
                elif len(json_contents) == 1 and 'id' in json_contents[0]:
                    person = Person(json_contents[0]['sei'], json_contents[0]['seiyomi'], json_contents[0]['mei'],
                                    json_contents[0]['meiyomi'], json_contents[0]['id'])
                    await self.feedback(f'{person.seiyomi}{person.meiyomi}???????????????',0)
                    personlist.append(person)
            idx += 1

        # if personList==[]:
        #     await self.feedback("???????????????????????????????????????",0)
        #     self.error = INF_NOT_HEAR_WELL
        #     return []
        return personlist

    async def interpret(self):
        print('AskName.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            return []
        if self.user.org == 'genkikai' and self.user.role == 'member' and \
                self.user.device == 'iPhone':  # and not self.user.capability_sr):
            print(f'interpret> button action detected: {selection}')
            # ["??????","?????????","??????","??????","??????"]
            if selection == '1':
                person = Person('??????', '?????????', '??????', '?????????', 'M0047')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '2':
                person = Person('?????????', '?????????', '?????????', '?????????', 'M0048')
                await self.feedback(f'{person.seiyomi}{person.meiyomi}???????????????', 0)
                return [person]
            elif selection == '3':
                person = Person('??????', '????????????', '??????', '????????????', 'M0027')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '4':
                person = Person('??????', '?????????', '??????', '?????????', 'M0098')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '5':
                person = Person('??????', '?????????', '?????????', '?????????', 'M0103', "U9eaedcaf69309ebb504bcadc344fc910")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '6':
                person = Person('???', '?????????', '?????????', '?????????', 'M0137', "U6b780e3bc04cb3fa7e868c73901d7531")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '7':
                person = Person('??????', '????????????', '??????', '?????????', 'M0141')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '8':
                person = Person('??????', '????????????', '??????', '?????????', 'M0142')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '9':
                person = Person('??????', '????????????', '??????', '????????????', 'M0168', "Ue25373ca7df45fd53d6cdbe1cc592953")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '10':
                person = Person('??????', '?????????', '?????????', '?????????', 'M0189')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
            elif selection == '11':
                person = Person('??????', '????????????', '?????????', '?????????', 'M0227')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}???????????????", 0)
                return [person]
        else:
            # if len(morphs)>0: await self.parse_name(morphs, self.person)
            return await self.parse_name(morphs)


class AskDate(Scene):
    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent

    async def prompt(self):
        print('AskDate.prompt')
        if self.error == com.INF_NOT_HEAR_WELL:
            speech = '???????????????????????????????????????'
            self.error = com.INF_RESET
        else:
            speech = '????????????????????????????????????'
        text = '????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + '}'
        await self.send_str(json_text)
        return
    
    def parse_month_day(self, morph1, morph2, day):
        if '???' == morph2['surface'] and 'pos' in morph1.keys() and morph1['pos'] == '?????????***':
            day.month = morph1['surface']
        if '???' == morph2['surface'] and 'pos' in morph1.keys() and morph1['pos'] == '?????????***':
            day.day = morph1['surface']

    async def parse_date(self, morphs):
        day = Day('', '', '', '')
        for idx, val in enumerate(morphs):
            if idx > 0: self.parse_month_day(morphs[idx - 1], morphs[idx], day)
        if any(['??????' in m['surface'] for m in morphs]):
            today = datetime.today()
            day.day = today.day
        elif any(['??????' in m['surface'] for m in morphs]):
            tomorrow = datetime.today() + 1
            day.year = tomorrow.year
            day.month = tomorrow.month
            day.day = tomorrow.day + 1
        elif any(['??????' in m['surface'] for m in morphs]):
            yesterday = datetime.today() - 1
            day.year = yesterday.year
            day.mopnth = yesterday.month
            day.day = yesterday.day
        if day.day != '':
            await self.feedback(f'{day.month}???{day.day}????????????',0)
            return day
        else:
            return SCENE_TERMINATE

    async def interpret(self):
        print('askDate.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            return SCENE_TERMINATE
        else:
            if len(morphs) > 0:
                return await self.parse_date(morphs)
            else:
                return SCENE_TERMINATE


class AskAmPm(Scene):
    def __init__(self, usr, parent, day):
        super().__init__(usr)
        self.parent = parent
        self.day = day

    async def prompt(self):
        print('AskAmPm.prompt')
        speech = '???????????????????????????????????????'
        text = '???????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + ',"suggestions":["??????","??????"]'+'}'
        await self.send_str(json_text)
        return
    
    async def parse_ampm(self, morphs, selection, dt):
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            dt.ampm = 'am'
            await self.feedback("??????????????????", 0)
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '2':
            dt.ampm = 'pm'
            await self.feedback("??????????????????",0)

    async def interpret(self):
        print('AskAmPm.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            return SCENE_TERMINATE
        else:
            await self.parse_ampm(morphs, selection, self.day)


class Reserve(Scene):

    def __init__(self, usr, reserve):
        super().__init__(usr)
        if reserve is None:
            self.reservation = Reservation()
        else:
            self.reservation = reserve
        self.operation = ''

    async def prompt(self):
        print('Reserve.prompt')
        self.error = com.INF_RESET
        if self.user.role == 'admin':
            speech = '?????????????????????????????????????????????????????????????????????????????????'
            text = '??????,??????,??????,??????????????????'
            json_text = '{' + f'"speech":"{speech}","text":"{text}",' +\
                        '"suggestions":["??????","??????","??????","???????????????","??????"]' + '}'  # ??????????????????????????????
            await self.send_str(json_text)
            return

    async def interpret(self):
        print('Reserve.interpret')
        if self.counter > 5:
            await self.feedback("???????????????",0)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("??????????????????????????????", 0)
            self.operation = 'add'
            return UpdateReservation(self.user, self)
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '2':
            self.operation = 'delete'
            await self.feedback("??????????????????????????????", 0)
            return UpdateReservation(self.user, self)
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '3':
            await self.feedback("?????????????????????????????????", 2)
            return await self.act_list_reservation()
        elif any(['??????' in m['surface'] for m in morphs]) or any(['??????' in m['surface'] for m in morphs]) or \
                any(['???????????????' in m['surface'] for m in morphs]) or selection == '4':
            await self.feedback("????????????????????????????????????????????????????????????LINE???????????????", 0)
            return await self.act_send_message()
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '5':
            await self.feedback("???????????????", 2)
            return SeeYou(self.user)
        else:
            self.error = com.INF_NO_TARGET_WORDS
            await self.feedback("????????????????????????????????????", 1)
            self.counter += 1
            return self

    async def act_list_reservation(self):
        print('act_list_reservation')
        await asyncio.sleep(2)
        url = 'https://npogenkikai.net/reservations/'
        json_text = '{' + f'"action":"goto_url","url":"{url}"' + '}'
        print(json_text)
        await self.send_str(json_text)
        return SCENE_LEAVE

    async def act_send_message(self):
        print('actSendMessage')
        self.reservation = Reservation()
        dt = AskDate(self.user, self)
        while self.reservation.date is None:
            self.reservation.date = await self.prompt_and_interpret(dt)
            if dt.error == com.ERR_TIMEOUT:
                await self.feedback("???????????????", 0)
                return SCENE_TERMINATE
        ap = AskAmPm(self.user, self, self.reservation.date)
        while self.reservation.date.ampm == '':
            await self.prompt_and_interpret(ap)
            if ap.error == com.ERR_TIMEOUT:
                await self.feedback("???????????????", 0)
                return SCENE_TERMINATE
        return SendReservationMessageS(self.user, self)


class UpdateReservation(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent
        self.reservation = parent.reservation
        self.operation = parent.operation

    async def prompt(self):
        print('UpdateReservation.prompt')
        speech = '?????????'
        text = ''
        display = ''
        if self.operation == "add":
            speech += '????????????'
        else:
            speech += '????????????'
        if self.reservation.date is None:
            speech += '????????????????????????'
            text += '????????????????????????'
        else:
            display = f'{self.reservation.date.month}???{self.reservation.date.day}???{self.reservation.date.ampm}'
        if not self.reservation.memberlist:
            speech += '?????????'
            if text != '':
                text += '?????????'
            else:
                text = '??????'
        else:
            display = ''
            for member in self.reservation.memberlist:
                display += f' {member.sei}{member.mei}???'
        speech += '???????????????????????????'
        text += '???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show":"{display}"' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('UpdateReservation.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        if self.reservation.date is None:
            dt = AskDate(self.user, self)
            self.reservation.date = await dt.parse_date(morphs)
            while self.reservation.date is None:
                self.reservation.date = await self.prompt_and_interpret(dt)
                if dt.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
        if self.reservation.date.ampm == '':
            ap = AskAmPm(self.user, self, self.reservation.date)
            await ap.parse_ampm(morphs,selection,self.reservation.date)
            while self.reservation.date.ampm == '':
                await self.prompt_and_interpret(ap)
                if ap.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
        if not self.reservation.memberlist:
            nm = AskName(self.user, self)
            self.reservation.memberlist = await nm.parse_name(morphs)
            while not self.reservation.memberlist:
                self.reservation.memberlist = await self.prompt_and_interpret(nm)
                if nm.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE

        return ConfirmReservation(self.user,self)


class ConfirmReservation(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent
        self.reservation = parent.reservation
        self.operation = parent.operation

    async def prompt(self):
        print('ConfirmReservation.prompt')
        if self.operation == "add":
            speech = '??????????????????????????????'
            text = '?????????'
        else:
            speech = '??????????????????????????????'
            text = '?????????'
        text += f'{self.reservation.date.month}???{self.reservation.date.day}???'
        if self.reservation.date.ampm == 'am':
            text += "??????"
        else:
            text += "??????"
        #TEXT += f':{self.reservation.member.sei}{self.reservation.member.mei}???'
        for member in self.reservation.memberlist:
            text += f',{member.sei}{member.mei}???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}", ' +\
                    '"suggestions":["??????","?????????","????????????","????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('ConfirmReservation.interpret')
        if self.counter > 5:
            await self.feedback("???????????????", 0)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        if selection == '1' or any(['??????' in m['surface'] for m in morphs]):
            return await self.act_update_reservation()
        elif selection == '2' or any(['?????????' in m['surface'] for m in morphs]):
            await self.feedback("????????????????????????", 0)
            return PostReservation(self.user, self)
        elif selection == '3' or any(['??????' in m['surface'] for m in morphs]):
            await self.feedback("????????????",0)
            self.parent.reservation = Reservation()
            self.parent.reservation.memberlist = self.reservation.memberlist
            return self.parent
        elif selection == '4' or any(['??????' in m['surface'] for m in morphs]):
            await self.feedback("????????????",0)
            self.parent.reservation = Reservation()
            self.parent.reservation.date = self.reservation.date
            return self.parent
        else:
            await self.feedback("????????????????????????????????????",1)
            self.counter += 1
            return self

    async def act_update_reservation(self):
        print('act_update_reservation')
        date = f'{self.reservation.date.year}/{self.reservation.date.month}/{self.reservation.date.day}'
        url = "https://npogenkikai.net/reserve.php"
        id_list = [m.id for m in self.reservation.memberlist]
        j = {"command": self.operation,"ids": id_list,"date": date,"ampm": self.reservation.date.ampm}
        print(f'{j}')
        th = threading.Thread(target=send_json_sync, args=([url, j]))
        th.start()
        #return SendReservationMessage(self.user,self)
        return PostReservation(self.user, self)


class PostReservation(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.reservation = parent.reservation

    async def prompt(self):
        print('PostReservation.prompt')
        speech = '???????????????????????????????????????????????????'
        text = '???????????????????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + ',"suggestions":["???????????????","??????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('PostReservation.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any([m['surface'].startswith('???') for m in morphs]) or \
                any([m['surface'].startswith('???') for m in morphs]) or selection == '1':
            await self.feedback("?????????????????????????????????????????????", 0)
            reservation = Reservation()
            reservation.date = self.reservation.date
            return Reserve(self.user, reservation)
        else:
            await self.feedback("???????????????",1)
            return SCENE_TERMINATE


class SendReservationMessageS(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.reservation = parent.reservation
        self.idList = []

    async def prompt(self):
        print('SendReservationMessageS.prompt')
        self.error = com.INF_RESET
        speech = '?????????????????????????????????????????????????????????????????????LINE?????????????????????????????????????????????'
        text = '?????????'
        date = f'{self.reservation.date.year}/{self.reservation.date.month}/{self.reservation.date.day}'
        self.idList = await send_json(
            "https://npogenkikai.net/reserve.php",
            {"command": "listbytimeslot", "date": date, "ampm": self.reservation.date.ampm}
        )
        lst = f'{self.reservation.date.month}???{self.reservation.date.day}???{self.reservation.date.ampm}?????????:<br>'
        for r in self.idList:
            print(f'{r}')
            userid = r['id']
            name_list = json.loads(
                names.nametable[(names.nametable['id'] == userid)]
                .to_json(orient="records", force_ascii=False)
            )
            print(f'cache: {name_list}')
            name = ''
            if len(name_list) == 1:
                name = name_list[0]
            elif len(name_list) == 0:
                name = await send_json("https://npogenkikai.net/id2name.php", {"id": userid})
                print(f'id2name: {name}')
            name_str = name['sei'] + name['mei']
            lst += ' ' + name_str
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show":"{lst}",' +\
                    '"suggestions":["??????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('SendReservationMessageS.interpret')
        if self.counter > 5:
            await self.feedback("???????????????",1)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("???????????????",0)
            return await self.act_send_message()
        elif any(['???????????????' in m['surface'] for m in morphs]) or selection == '2':
            await self.feedback("?????????????????????????????????",0)
            return Reserve(self.user, None)
        else:
            self.error = com.INF_NO_TARGET_WORDS
            await self.feedback("????????????????????????????????????",1)
            self.counter += 1
            return self

    async def act_send_message(self):
        print('actSendMessage')
        print(f'{self.idList}')
        sent = ''
        notsent = ''
        for r in self.idList:
            userid = r['id']
            lineid = ''
            name_str = ''
            json_contents = json.loads(
                names.nametable[(names.nametable['id'] == userid)]
                .to_json(orient="records", force_ascii=False)
            )
            if len(json_contents) == 1:
                name = json_contents[0]
                name_str = name['sei'] + name['mei']
                lineid = name['lineid']
            elif len(json_contents) == 0:
                #json_contents = await sendJson("https://npogenkikai.net/id2lineid.php",{"userid":userid})
                name = await send_json("https://npogenkikai.net/id2name.php", {"id": userid})
                name_str = name['sei'] + name['mei']
                lineid = name['lineid']
            print(lineid, name_str)
            if lineid != '':
                message = f'(??????????????????) {name_str}??????'
                message += f'????????????????????????????????????{self.reservation.date.month}???' +\
                           f'{self.reservation.date.day}???{self.reservation.date.ampm}????????????????????????????????????'
                message += '??????????????????????????? https://npogenkikai.net/?openExternalBrowser=1 ???????????????????????????????????????????????????????????????'
                th = threading.Thread(target=send_to_line, args=([lineid, message]))
                th.start()
                print(message)
                sent += name_str + ','
            else:
                #message = f'LINE???ID???????????????????????????????????????????????????????????????????????????{nameStr}?????????LINEID???????????????????????????'
                #th = threading.Thread(target=sendToLine, args=([None, message]))
                #th.start()
                #print(message)
                notsent += name_str + ','
        # send a log to admin at once
        admin_message = '[???????????????]\n' + sent + '??????????????????'\
            + f'(??????????????????) X??????'\
              + f'????????????????????????????????????{self.reservation.date.month}???{self.reservation.date.day}' +\
                        '???{self.reservation.date.ampm}????????????????????????????????????' +\
                        '??????????????????????????? https://npogenkikai.net/?openExternalBrowser=1 ???????????????????????????????????????????????????????????????' +\
                        '??????????????????????????????'
        admin_message += '\n???????????????LINEID?????????????????????????????????????????????????????????????????????' + notsent
        th = threading.Thread(target=send_to_line, args=([None, admin_message]))
        th.start()
        print(admin_message)
        return Reserve(self.user, None)


class Record(Scene):

    def __init__(self, usr, visit):
        super().__init__(usr)
        if visit is None:
            self.visit = Visit()
        else:
            self.visit = visit
        self.operation = ''

    async def prompt(self):
        print('Record.prompt')
        self.error = com.INF_RESET
        if self.user.role == 'admin':
            speech = '??????????????????????????????????????????????????????????????????????????????'
            text = '??????,??????,?????????,?????????'
            json_text = '{' + f'"speech":"{speech}","text":"{text}",' +\
                        '"suggestions":["??????","??????","?????????","??????","??????"]' + '}'  # ??????????????????????????????
            await self.send_str(json_text)
            return

    async def interpret(self):
        print('cord.interpret')
        if self.counter > 5:
            await self.feedback("???????????????", 0)
            return SCENE_TERMINATE
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return
        if any(['??????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("????????????????????????????????????", 0)
            self.operation = 'add'
            return UpdateRecord(self.user, self)
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '2':
            self.operation = 'delete'
            await self.feedback("????????????????????????????????????", 0)
            return UpdateRecord(self.user, self)
        elif any(['?????????' in m['surface'] for m in morphs]) or selection == '3':
            await self.feedback("?????????????????????????????????????????????", 0)
            return Reservation2Record(self.user,self)
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '4':
            await self.feedback("???????????????????????????????????????", 2)
            return await self.act_list_record()
        elif any(['??????' in m['surface'] for m in morphs]) or selection == '5':
            await self.feedback("???????????????", 2)
            return SeeYou(self.user)
        else:
            self.error = com.INF_NO_TARGET_WORDS
            await self.feedback("????????????????????????????????????", 1)
            self.counter += 1
            return self

    async def act_list_record(self):
        print('actListRecord')
        await asyncio.sleep(2)
        url = 'https://npogenkikai.net/allrecords/'
        json_text = '{' + f'"action":"goto_url","url":"{url}"' + '}'
        print(json_text)
        await self.send_str(json_text)
        return SCENE_LEAVE


class Reservation2Record(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.user = usr
        self.parent = parent

    async def prompt(self):
        print('Reservation2Record.prompt')
        speech = '????????????????????????????????????????????????'
        text = '????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('Reservation2Record.interpret')
        sts, json_dict, morphs, selection = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        dt = AskDate(self.user, self)
        date = await dt.parse_date(morphs)
        while date is None:
            date = await self.prompt_and_interpret(dt)
            if dt.error == com.ERR_TIMEOUT:
                await self.feedback("???????????????", 0)
                return SCENE_TERMINATE

        return ConfirmReservation2Record(self.user, date)


class ConfirmReservation2Record(Scene):

    def __init__(self, usr, date):
        super().__init__(usr)
        self.user = usr
        self.date = date

    async def prompt(self):
        print('ConfirmReservation2Record.prompt')
        speech = f'{self.date.year}???{self.date.month}???{self.date.day}????????????????????????????????????'
        text = f'{self.date.year}/{self.date.month}/{self.date.day}???????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","suggestions":["?????????","???????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('ConfirmReservation2Record.interpret')
        sts, json_dict, morphs, selection = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        if any(['?????????' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("??????????????????",0)
            url = 'https://npogenkikai.net/reservation2record.php?date=' + \
                  f'{self.date.year}/{self.date.month}/{self.date.day}'
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                _ = resp.read()  # just ignore returned text
            # await sendGetRequest(url)
            await self.feedback("?????????????????????", 0)
        elif any(['???????????????' in m['surface'] for m in morphs]) or selection == '2':
            await self.feedback("????????????????????????",0)
        return SCENE_TERMINATE


class UpdateRecord(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent
        self.visit = parent.visit
        self.operation = parent.operation

    async def prompt(self):
        print('UpdateRecord.prompt')
        speech = '???????????????'
        text = ''
        display = ''
        if self.operation == "add":
            speech += '????????????'
        else:
            speech += '????????????'
        if self.visit.date is None:
            speech += '?????????'
            text += '?????????'
        else:
            display = f'{self.visit.date.month}???{self.visit.date.day}???'
        # if self.reservation.member.userid == '':
        if not self.visit.memberlist:
            speech += '?????????'
            if text != '':
                text += '?????????'
            else:
                text = '??????'
        else:
            display = ''
            for member in self.visit.memberlist:
                display += f' {member.sei}{member.mei}???'
        speech += '???????????????????????????'
        text += '???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}","show":"{display}"' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('UpdateRecord.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        if self.visit.date is None:  # date maybe already filled
            dt = AskDate(self.user, self)
            self.visit.date = await dt.parse_date(morphs)
            while self.visit.date is None:
                self.visit.date = await self.prompt_and_interpret(dt)
                if dt.error == com.ERR_TIMEOUT:
                    await self.feedback("???????????????", 0)
                    return SCENE_TERMINATE
        nm = AskName(self.user, self)
        self.visit.memberlist = await nm.parse_name(morphs)
        while not self.visit.memberlist:
            self.visit.memberlist = await self.prompt_and_interpret(nm)
            if nm.error == com.ERR_TIMEOUT:
                await self.feedback("???????????????", 0)
                return SCENE_TERMINATE
            if self.error == com.ERR_TIMEOUT:
                return SCENE_TERMINATE

        return ConfirmRecord(self.user, self)


class ConfirmRecord(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.parent = parent
        self.visit = parent.visit
        self.operation = parent.operation

    async def prompt(self):
        print('ConfirmRecord.prompt')
        if self.operation == "add":
            speech = '??????????????????????????????'
            text = '?????????'
        else:
            speech = '??????????????????????????????'
            text = '?????????'
        text += f'{self.visit.date.month}???{self.visit.date.day}???'
        for member in self.visit.memberlist:
            text += f',{member.sei}{member.mei}???'
        json_text = '{' + f'"speech":"{speech}","text":"{text}", ' +\
                    '"suggestions":["??????","?????????","????????????","????????????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('ConfirmRecord.interpret')

        if self.counter > 5:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE

        if selection == '1' or any(['??????' in m['surface'] for m in morphs]):
            return await self.act_update_record()
        elif selection == '2' or any(['?????????' in m['surface'] for m in morphs]):
            await self.feedback("????????????????????????", 0)
            return PostRecord(self.user, self)
        elif selection == '3' or any(['??????' in m['surface'] for m in morphs]):
            await self.feedback("????????????", 0)
            self.parent.visit = Visit()
            self.parent.visit.memberlist = self.visit.memberlist
            return self.parent
        elif selection == '4' or any(['??????' in m['surface'] for m in morphs]):
            await self.feedback("????????????", 0)
            self.parent.visit = Visit()
            self.parent.visit.date = self.visit.date
            return self.parent
        else:
            await self.feedback("????????????????????????????????????", 1)
            self.counter += 1
            return self

    async def act_update_record(self):
        print('actUpdateRecord')
        date = f'{self.visit.date.year}/{self.visit.date.month}/{self.visit.date.day}'
        url = "https://npogenkikai.net/record.php"
        id_list = [m.id for m in self.visit.memberlist]
        th = threading.Thread(target=send_json_sync,
                              args=([url, {"command": self.operation, "ids": id_list, "date": date}]))
        th.start()
        return PostRecord(self.user, self)


class PostRecord(Scene):

    def __init__(self, usr, parent):
        super().__init__(usr)
        self.visit = parent.visit

    async def prompt(self):
        print('PostRecord.prompt')
        speech = '?????????????????????????????????????????????????????????'
        text = '???????????????????????????'
        json_text = '{' + f'"speech":"{speech}","text":"{text}"' + ',"suggestions":["???????????????","??????"]' + '}'
        await self.send_str(json_text)
        return

    async def interpret(self):
        print('PostRecord.interpret')
        sts, json_dict, morphs, selection, intent = await self.decode_response()
        if sts != com.SUCCESS:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE
        if any([m['surface'].startswith('???') for m in morphs]) or any(
                [m['surface'].startswith('???') for m in morphs]) or selection == '1':
            await self.feedback("???????????????????????????????????????????????????", 0)
            visit = Visit()
            visit.date = self.visit.date
            return Record(self.user, visit)
        else:
            await self.feedback("???????????????", 1)
            return SCENE_TERMINATE


class SeeYou(Scene):

    async def prompt(self):
        print('SeeYou.prompt')

    async def interpret(self):
        print('SeeYou.interpret')
        speech = '?????????'
        text = '?????????'
        json_text = '{' + f'"feedback":"{speech}","text":"{text}"'+'}'
        await self.send_str(json_text)
        await asyncio.sleep(2)
        #jsonText = '{' + f'"action":"finish"'+'}'
        #await self.sendStr(jsonText)
        return SCENE_TERMINATE


async def close_websockets():
    global user

    #user: User
    # clean up client
    if user.ws is not None and not user.ws.closed:
        await asyncio.sleep(1)  # time to get 'finish' echo back log
        await user.ws.close()
    print('user.close_websockets > Websocket connections closed')


async def on_shutdown(app):
    print('on_shutdown >... ')
    await close_websockets()
    print('on_shutdown > manager.cleanup')
    await app.cleanup()


def termination_handler(signal,frame):
    sys.exit(0)


DEBUG = True
line_bot_api = None
line_parser = None
app = None
user = None


def main(user_port, org, role, invoker, child_conn):

    global line_parser
    global line_bot_api
    global app
    global user

    print('user is up and running')
    signal.signal(signal.SIGINT, termination_handler)
    signal.signal(signal.SIGTERM, termination_handler)
    user = User(user_port, org, role, invoker, child_conn)
    print(f'user main > user port:{user.wsPort},org:{user.org},role:{user.role},invoker:{user.invoker}')

    line_bot_api = LineBotApi(line_config.LINE_CHANNEL_ACCESS_TOKEN)
    line_parser = WebhookParser(line_config.LINE_CHANNEL_SECRET)

    app = None
    ctx = None
    if config.PROTOCOL == "http":
        pass
    else:
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        if config.CLOUD_INSTANCE:
            ctx.load_cert_chain('/etc/letsencrypt/live/rakudana.com/fullchain.pem',
                                keyfile='/etc/letsencrypt/live/rakudana.com/privkey.pem')
        else:
            ctx.load_cert_chain('server.crt', keyfile='server.key')
        ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_3
        ctx.check_hostname = False

    try:
        logger = logging.getLogger('aiohttp.access')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        logger.addHandler(ch)

        print("user.main > starts web socket handler for client browser")

        loop = asyncio.get_event_loop()
        app = web.Application(logger=logger, loop=loop)
        #?????????????
        app.router.add_route('GET', '/ws/b', browser_handler)
        app.router.add_route('GET', '/ws/a', app_handler)
        #app.router.add_route('POST', '/post', post_handler)
        #???????????????
        app.on_shutdown.append(on_shutdown)

        # threading.Thread(target=on_startup, args=([manager])).start()

        if config.PROTOCOL == "http":
            web.run_app(app, host=ip_config.HOST_INTERNAL_IP, port=user.wsPort)
        else:
            web.run_app(app, host=ip_config.HOST_INTERNAL_IP, port=user.wsPort, ssl_context=ctx)

    except Exception as e:
        print('user.main > exception {}'.format(e))
        print(traceback.format_exc())

    finally:
        print('user.main > finally')
        #user.pipe.send('finish$')
        history = [x.__class__.__name__ for x in user.dialog_history]
        print(f'[DIALOG] HISTORY: {history}')
        # time.sleep(2) # for shutdown cor to execute
        # sys.exit(0)
