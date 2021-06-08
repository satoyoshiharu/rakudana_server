"""
 UI, Communication controller
 Process per user
"""
import aiohttp.web
import concurrent.futures
import time
from multiprocessing import Process, Pipe, Queue
import traceback
import signal
import sys
import os.path
import config
import json
import ssl
import MeCab
import urllib.request
import logging
import re
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent, SourceUser
from datetime import datetime, date, timedelta
import asyncio
import pandas as pd
import threading
import re
import names
from ner import NER
import sentencepiece as spm
from gensim.models import KeyedVectors
import torch
from intent_classifier import train
from intent_classifier import create_training_data

DEBUG = True

INF_OK = 0
INF_RESET = 1
INF_NOT_HEAR_WELL = 2
INF_NO_MATCHING_NAME  = 3
INF_NO_TARGET_WORDS = 4
INF_MULTIPLE_MATCH = 5

SUCCESS = 0
ERR_EXCEPTION = 1
ERR_TIMEOUT = 2
ERR_TYPEERROR = 3

tagger = None
tokenizer = None
wv = None
intent_classifier = None

class Person():
    def __init__(self, sei, seiyomi, mei, meiyomi, id, lineid):
        self.sei = sei
        self.seiyomi = seiyomi
        self.mei = mei
        self.meiyomi = meiyomi
        self.id = id
        self.lineid = lineid


class User():
    def __init__(self, port, org, role, invoker):
        global tagger
        self.wsPort = int(port)
        self.ws = None
        self.monitorInfo = None
        self.org = org
        self.role = role
        self.invoker = invoker
        self.person = None
        #self.tagger = MeCab.Tagger("-O dump -r /dev/null -d /usr/share/mecab/dic/ipadic/")
        #self.tagger = MeCab.Tagger("-O dump")
        #self.tagger = MeCab.Tagger()
        #parsed = self.tagger.parse('私') # preload dictionary
        #self.tagger = tagger
        self.dialog_history = []
        self.device = ''
        self.capability_sr = False
        self.capability_ss = False
        self.screen_width = 0
        self.screen_height = 0
        self.cookie = ''
        if self.invoker == 'rakudana_app':
            self.ner = NER()

    def cookie2id(self):
        print(f'cookie2id > {self.cookie}')
        if self.cookie!='':
            id = re.findall(r'genkikai_id\=([^,]*)', self.cookie)
            print(f'cookie2id > {id[0]}')
            return id[0]
        else:
            return ''


class Day():
    def __init__(self,year,month,day,ampm):
        today = datetime.today()
        if year!='':
            self.year = year
        else:
            self.year = today.year
        if month!='':
            self.month = month
        else:
            self.month = today.month
        self.day = day
        self.ampm = ampm

class Reservation():
    def __init__(self):
        self.date = None
        self.memberList = []
        #self.member = Person('','','')

class Visit():
    def __init__(self):
        self.date = None
        self.memberList = []

#flag_started = False

async def browser_handler(request):
    #global flag_started

    print('browser_handler > Websocket connection starting')
    #flag_started = True
    user.ws = aiohttp.web.WebSocketResponse(timeout=60, max_msg_size=256)
    await user.ws.prepare(request)
    print('browser_handler > Websocket connection ready')

    #r = await user.ws.receive()
    #jsonDict = json.loads(r.data)
    sts, jsonDict = await recvJson(user.ws)
    if sts==SUCCESS:
        print(f'received: {jsonDict}')

        if 'device' in jsonDict: user.device = jsonDict['device']
        if 'capability_ss' in jsonDict and jsonDict['capability_ss']=='1': user.capability_ss = True
        if 'capability_sr' in jsonDict and jsonDict['capability_sr']=='1': user.capability_sr = True
        if 'screen_width' in jsonDict: user.screen_width = int(jsonDict['screen_width'])
        if 'screen_height' in jsonDict: user.screen_height = int(jsonDict['screen_height'])
        if 'cookie' in jsonDict: user.cookie = jsonDict['cookie']

        conversation = ConversationModel(user)
        await conversation.loop()

    print('user.browser_handler > Websocket connection closed')
    user.ws.force_close()
    #print(user.dialog_history)
    sys.exit(0)
    #return user.ws

class ConversationModel():

    def __init__(self, user):
        self.user = user

    async def loop(self):
        json = '{"feedback":"開始します"}'
        await self.user.ws.send_str(json)
        await asyncio.sleep(1)

        scene = Initial(self.user)
        self.user.dialog_history.append(scene)
        while True:
            try:
                await scene.prompt()
                # NER detection and Intent detection are done in decode_response
                scene = await scene.interpret()
                print(f'scene: {scene.__class__.__name__}')
                # (1) explicit termination (2) timeout error (idle >10 minutes)
                if scene==None:
                    #await asyncio.sleep(10000)
                    jsonText = '{' + f'"action":"finish"' + '}'
                    if not self.user.ws.closed: await self.user.ws.send_str(jsonText)
                    return
                self.user.dialog_history.append(scene)
            except Exception as e:
                # maybe timeout error
                print(f'ConversationModel.loop > exception: {e}')
                print(traceback.format_exc())
                jsonText = '{' + f'"action":"finish"' + '}'
                if not self.user.ws.closed: await self.user.ws.send_str(jsonText)
                return # -> finish

def sendJson_sync(url,data):
    print(f'sendJson > {url}, {data}')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        print('respose: ', res)
        json_contents = json.load(res)
        print('json contents', json_contents)

async def sendJson(url,data):
    print(f'sendJson > {url}, {data}')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        print('respose: ', res)
        #try:
        json_contents = json.load(res)
        print('json contents', json_contents)
        return json_contents
        #except Exception as e:
        #    print(traceback.format_exc())
        #    return {}

def sendToLine(lineid, message):
    if lineid != None:
        line_bot_api.push_message(lineid, TextSendMessage(text=message))
        print(f'sent to {lineid}: {message}')
    else:
        line_bot_api.push_message(config.LINE_ADMIN_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(config.LINE_ADMIN2_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(config.LINE_ADMIN3_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(config.LINE_ADMIN4_USERID, TextSendMessage(text=message))

def detect_intent(text):
    print('detect_intent > ...')
    input = torch.tensor(
        create_training_data.embAvg(text, tokenizer, wv),
        dtype=torch.float
    )
    intent_classifier.eval()
    with torch.no_grad():
        intent = torch.argmax(intent_classifier(torch.unsqueeze(input, 0))).item()
    print(f'detect_intent> {config.intents[intent]}')
    return intent

async def recvJson(ws):

    async def receive_json(ws):
        try:
            while True:
                r = await ws.receive()
                print(f'recvJson > received (raw): {r.data}')
                if type(r.data) is int:
                    print(f'recvJson > int returned {r.data}')
                    return ERR_TYPEERROR, None
                jsonDict = json.loads(r.data)
                if len(r.data) == 0:
                    continue
                #print(f'recvJson > received(json): {jsonDict}')
                if 'status' in jsonDict:
                    continue
                else:
                    break
            return SUCCESS, jsonDict
        # except json.decoder.JSONDecodeError:
        #     print('JsonDecode Exception in recvJson')
        #     print(traceback.format_exc())
        #     return {} #-> continue
        except TypeError:
            print('TypeError Exception in recvJson')
            print(traceback.format_exc())
            # ignore
            # await self.recvJson();
            return ERR_TYPEERROR, None  # -> continue
        except Exception as e:
            print(f'Exception in recvJson: {e}')
            print(traceback.format_exc())
            return ERR_EXCEPTION, None

    print('recvJson')
    try:
        sts, jsonDict = await asyncio.wait_for(receive_json(ws), config.RECVJSON_TIMEOUT)
    except asyncio.TimeoutError:
        sts, jsonDict = ERR_TIMEOUT, {}
        print(jsonDict)
    return sts, jsonDict

class Scene():

    def __init__(self, user):
        self.user = user
        self.ws = self.user.ws
        self.tagger = self.user.tagger
        self.error = INF_OK
        self.counter = 0

    def getMorphs(self, jsonDict):
        v = jsonDict['recognized']
        parsed = self.tagger.parse(v)
        morphs = []
        for token in parsed.split('\n'):
            #attr = token.split('\t')
            attr = re.split('[\t,]', token)
            if DEBUG: print(f'getMorphs > attr: {attr}')
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

    async def sendStr(self, json):
        print(f'sendStr > {json}')
        try:
            if not self.ws.closed: await self.ws.send_str(json)
        except Exception as e:
            print('sending > exception {}'.format(e))
            print(traceback.format_exc())
            #print(f'{user.dialog_history}')
            exit(1)

    async def prompt_and_interpret(self, scene):
        await scene.prompt()
        if scene.counter > 5:
            #await self.sendStr('{"feedback":"終了します"}')
            scene.error = ERR_TIMEOUT
            return None
        scene.counter += 1
        return await scene.interpret()

    async def decode_response(self):
        print('decode_response')
        sts, jsonDict = await recvJson(self.ws)
        if sts != SUCCESS:
            return sts, None, None, None, None
        morphs = []
        selection = ''
        intent = None
        if 'recognized' in jsonDict:
            morphs = self.getMorphs(jsonDict)

            if self.user.invoker == 'rakudana_app':
                # detect entities for following processing
                self.user.ner.findEntity(morphs)
                # detect intention
                intent = detect_intent(jsonDict['recognized'])

        if 'action' in jsonDict and jsonDict['action'] == 'button':
            selection = jsonDict['selection']
            print(f'confirmFinish> button action detected: {selection}')

        return sts, jsonDict, morphs, selection, intent

    async def feedback(self,msg,pause):
        await self.sendStr('{"feedback":"' + f'{msg}' + '"}')
        if pause>0: await asyncio.sleep(pause)


class Initial(Scene):

    async def prompt(self):
        print('Initial.prompt')
        if self.error == INF_NO_TARGET_WORDS:
            SPEECH = 'ご要件は？'
            self.error = INF_RESET
        else:
            SPEECH = 'げんきですか、ご要件は？'
        TEXT = 'ご要件は？'

        if self.user.invoker == 'rakudana_app':
            DISPLAY = 'できること：電話、LINEでメッセージ送信。'
            jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","show": "{DISPLAY}"' + '}'

        elif self.user.org == 'genkikai':
            if self.user.role == 'admin':
                jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","suggestions":["予約管理","来場記録","終了"]' + '}'
            else:
                jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","suggestions":["予約確認","お知らせ","ポイント","終了","その他"]' + '}'

        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('Initial.interpret')
        if self.counter > 5:
            await self.feedback("終了します",1)
            return None
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            await self.feedback("終了します", 1)
            return None

        if self.user.invoker == 'rakudana_app':
            if intent == config.INTENT_TEL:
                await self.feedback("電話ですね", 0)
                #return MakeACall(self.user)
                return await self.actMakeACall()

        elif self.user.org == 'genkikai':
            if self.user.role == 'admin':
                if any(['予約' in m['surface'] for m in morphs]) or selection=='1':
                    await self.feedback("予約を管理します",0)
                    return Reserve(self.user, None)
                if any(['履歴' in m['surface'] for m in morphs]) or any(['来場' in m['surface'] for m in morphs]) \
                        or any(['記録' in m['surface'] for m in morphs]) or selection=='2':
                    await self.feedback("来場者記録を管理します",0)
                    return Record(self.user, None)
                elif any(['終了' in m['surface'] for m in morphs]) or selection=='3':
                    await self.feedback("終了します",0)
                    return SeeYou(self.user)
                #elif any(['転送' in m['surface'] for m in morphs]) or selection=='2':
                #    await self.sending('{"feedback":"来場記録を管理します"}')
                #    return TransferRecord_step1Receive(self.user)
                else:
                    self.error = INF_NO_TARGET_WORDS
                    self.counter += 1
                    await asyncio.sleep(1)
                    return self
            else:
                if any(['予約' in m['surface'] for m in morphs]) or selection=='1':
                    await self.feedback("予約を表示します",0)
                    return await self.actMyReservation()
                elif any(['知ら' in m['surface'] for m in morphs]) or selection=='2':
                    await self.feedback("お知らせページを開きます",2)
                    return await self.actNews()
                # elif any(['コード' in m['surface'] for m in morphs]) or selection=='3':
                #     await self.sending('{"feedback":"個人コードを表示します"}')
                #     return await self.actMyCode()
                elif any(['ポイント' in m['surface'] for m in morphs]) or selection=='3':
                    await self.feedback("ポイントを表示します",0)
                    return await self.actMyPoint()
                elif any(['終了' in m['surface'] for m in morphs]) or selection=='4':
                    await self.feedback("終了します",0)
                    return SeeYou(self.user)
                elif any(['他' in m['surface'] for m in morphs]) or selection=='5':
                    return Secondary(self.user, self)
                else:
                    self.error = INF_NO_TARGET_WORDS
                    await self.sendStr('{"feedback":"よく聞き取れませんでした。"}')
                    self.counter += 1
                    await asyncio.sleep(1)
                    return self

    async def actMakeACall(self):
        print('actMakeACall')
        URL = 'apps://rakudana.com/client_app/make_a_call'
        jsonText = '{' + f'"action":"invoke_app","url":"{URL}"' + '}'
        print(jsonText)
        await self.sendStr(jsonText)
        return None

    async def id2person(self, id):
        print(f'id2person>{id}')
        if id=='': return None
        json_contents = \
            json.loads(pdNames[(pdNames['id'] == id)].to_json(orient="records", force_ascii=False))
        print(f'id2person > cache returns {json_contents}')
        if len(json_contents) > 0:
            print(f'id2person > hit cache {json_contents}')
            json_contents = json_contents[0]
        else:
            json_contents = await sendJson("https://npogenkikai.net/id2name.php",{"id": id})
            print(f'id2person > id2name returns {json_contents}')
        person = Person(json_contents['sei'], json_contents['seiyomi'],
                        json_contents['mei'], json_contents['meiyomi'],
                        id, json_contents['lineid'])
        await self.feedback(f'{person.seiyomi}{person.meiyomi}様ですね？', 0)
        return person

    async def actMyReservation(self):
        print('actMyReservation')
        id = self.user.cookie2id()
        if id!='':
            self.user.person = await self.id2person(id)
        else:
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error==ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
                if len(persons)==1: self.user.person = persons[0]
        #await self.feedback("予約登録状況を表示します。",2)
        URL = 'https://npogenkikai.net/reservations?id=' + self.user.person.id
        jsonText = '{' + f'"action":"goto_url","url":"{URL}"' + '}'
        await self.sendStr(jsonText)
        return None

    async def actMyCode(self):
        print('actMyCode')
        id = self.user.cookie2id()
        if id!='':
            self.user.person = await self.id2person(id)
        else:
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error==ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
                if len(persons)==1: self.user.person = persons[0]
        #return ShowMyCode(self.user)
        #await self.feedback("個人コードを表示します。",2)
        URL = 'https://npogenkikai.net/myqrcode?id=' + self.user.person.id
        jsonText = '{' + f'"action":"goto_url","url":"{URL}"' + '}'
        await self.sendStr(jsonText)
        return None

    async def actNews(self):
        print('actNews')
        URL = 'https://npogenkikai.net/news'
        jsonText = '{' + f'"action":"goto_url","url":"{URL}"' + '}'
        await self.sendStr(jsonText)
        return None
        #return ViewInlineFrame(self.user, URL)

    async def actMyPoint(self):
        print('actMyPoint.react')
        id = self.user.cookie2id()
        if id!='':
            self.user.person = await self.id2person(id)
        else:
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error==ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
                if len(persons)==1: self.user.person = persons[0]

        URL = 'https://npogenkikai.net/mypoints2?id=' + self.user.person.id
        jsonText = '{' + f'"action":"goto_url","url":"{URL}"' + '}'
        await self.sendStr(jsonText)
        return None
        #return ViewInlineFrame(self.user, URL)

class Secondary(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.user = user
        self.parent = parent

    async def prompt(self):
        print('Secondary.prompt')
        SPEECH = 'お名前で登録すると、「げんきかい」のメンバーIDをスマホに記録します。このIDは、この対話サイトだけからみえる識別情報です。'
        if self.user.device == 'iPhone':
            SPEECH += '事前に、設定、Safari、プライバシーとセキュリティ、でクッキーをONにしてからおこなって下さい。'
        TEXT = '氏名登録'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","suggestions":["氏名登録","戻る"]' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('Secondary.interpret')
        if self.counter > 5:
            await self.feedback("終了します",1)
            return None
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            await self.feedback("終了します", 1)
            return None
        if any(['登録' in m['surface'] for m in morphs]) or selection=='1':
            await self.feedback("登録します。",0)
            nm = AskName(self.user, self)
            while self.user.person is None:
                persons = await self.prompt_and_interpret(nm)
                if nm.error == ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
                if persons!=[] and len(persons) == 1:
                    self.user.person = persons[0]
            # store ID in client brwoser as Cookie
            # max-age is 60 days->5184000
            cookie = f'genkikai_id={self.user.person.id}; host={config.HOST_EXTERNAL_IP}; path=/; max-age=5184000; secure; SameSite=Strict;'
            jsonText = '{' + f'"action":"set_cookie","cookie":"{cookie}"' + '}'
            await self.sendStr(jsonText)
            await self.feedback("スマホにIDを記録しました。",2)
            self.user.cookie = f'genkikai_id={self.user.person.id}'
            return self.parent
        elif any([m['surface'].startswith('戻') for m in morphs]) or selection=='2':
            await self.feedback("戻ります。",0)
            return self.parent
        else:
            self.error = INF_NO_TARGET_WORDS
            self.counter += 1
            await asyncio.sleep(1)
            return self


class MakeACall(Scene):

    async def prompt(self):
        print('MakeACall.prompt')
        return

    async def interpret(self):
        print('MakeACall.interpret')
        URL = 'https://rakudana.com/app/make_a_call'
        jsonText = '{' + f'"action":"invoke_app","url":"{URL}"' + '}'
        print(jsonText)
        await self.sendStr(jsonText)
        return None


pdNames = pd.DataFrame(data=names.names, columns=["id","sei","seiyomi","mei","meiyomi","lineid"])

class AskName(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.parent = parent

    async def prompt(self):
        print('AskName.prompt')
        if self.error == INF_NO_MATCHING_NAME:
            SPEECH = '再度、お名前をはっきりとお話下さい。または、担当者にご連絡下さい。'
            self.error = INF_RESET
        elif self.error == INF_NOT_HEAR_WELL:
            SPEECH = '再度、お名前をお話下さい。'
            self.error = INF_RESET
        elif self.error == INF_NO_TARGET_WORDS:
            SPEECH = '姓もしくは姓名を下さい。'
        else:
            SPEECH = 'お名前をください。'
        TEXT = 'お名前（姓名）は？'
        if (self.user.org=='genkikai' and self.user.role=='member' and not self.user.capability_sr):
            jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","suggestions":["小川","小木曾","今村","佐藤佳","島田","所","中越","中島","久留","馬渕寿","渡辺美"]' + '}'
        else:
            jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}"' + '}'
        await self.sendStr(jsonText)
        return

    def parse_seimei(self, morph1, morph2):
        print(f'parse_seimei > {morph1}, {morph2}')
        if len(morph1)>1 and 'pos' in morph1.keys() and morph1['pos'] == '名詞固有名詞人名姓*' and\
                'pos' in morph2.keys() and morph2['pos'] == '名詞固有名詞人名名*':
            print(f'parse_seimei > found sei mei candidate')
            return morph1['surface'], morph1['base'], morph2['surface'], morph2['base']
        else:
            return '','','',''

    def parse_mei(self, morph):
        print(f'parse_mei > {morph}')
        if 'pos' in morph.keys() and (morph['pos'] == '名詞固有名詞人名姓*' or morph['pos'].startswith('名詞固有名詞')):
            print(f'parse_mei > found sei candidate')
            if 'base' in morph:
                return morph['surface'], morph['base']
            else:
                return '',''
        else:
            return '',''

    async def parse_name(self, morphs):
        print(f'parse_name > {morphs}')
        json_contents = ''
        personList = []
        idx = 0
        while True:
            if idx == len(morphs): break
            sei, seiyomi, mei, meiyomi = '', '','',''
            if idx + 1 <= len(morphs) - 1:
                sei, seiyomi, mei, meiyomi = self.parse_seimei(morphs[idx], morphs[idx + 1])
            if seiyomi != '' and meiyomi != '':
                # try pdNames cache first
                json_contents = \
                    json.loads(pdNames[(pdNames['seiyomi'] == seiyomi) & (pdNames['meiyomi'] == meiyomi)].to_json(
                        orient="records", force_ascii=False))
                print(f'parse_name > cache returns {json_contents}')
                if len(json_contents) > 0:
                    print(f'parse_name > yomi hit cache {json_contents}')
                else:
                    #たけうち->SR returns ’竹内', base'たけうち’ -> here try to match base form'たけうち' against DB.
                    # Mostly it works to register surface form which SR recognized as user word of Mecab.
                    json_contents = await sendJson("https://npogenkikai.net/name2id.php",
                                                        {"seiyomi": seiyomi,
                                                         "meiyomi": meiyomi})
                    print(f'parse_name > with yomi, name2id returns {json_contents}')
                    # try to match ’竹内’
                    if len(json_contents):
                        json_contents = await sendJson("https://npogenkikai.net/name2id.php",
                                                       {"sei": sei,
                                                        "meiyomi": meiyomi})
                        print(f'parse_name > with hyouki, name2id returns {json_contents}')
                idx += 1
            else:
                # try with sei only
                sei, seiyomi = self.parse_mei(morphs[idx])
                if seiyomi != '':
                    json_contents = json.loads(pdNames[ pdNames['seiyomi']==seiyomi ].to_json(orient="records", force_ascii=False))
                    if len(json_contents) > 0:
                        print(f'parse_name > cache returns {json_contents}')
                    else:
                        json_contents = await sendJson("https://npogenkikai.net/name2id.php",
                                                        {"seiyomi": seiyomi})
                        print(f'parse_name > name2id returns {json_contents}')
            if seiyomi!='':
                if json_contents==[] or json_contents=='' or 'error' in json_contents:
                    if meiyomi!='':
                        await self.feedback(seiyomi + meiyomi + '様のお名前が見つかりませんでした', 0)
                    else:
                        await self.feedback(seiyomi + '様のお名前が見つかりませんでした',0)
                    self.error = INF_NO_MATCHING_NAME
                    return []
                elif len(json_contents) > 1:
                    multiple_mei = ' '.join([c['meiyomi']+'さま' for c in json_contents])
                    await self.feedback(seiyomi + 'さまに、複数の該当者がいます。'+multiple_mei+'です。名前もご指定下さい。',0)
                    self.error = INF_MULTIPLE_MATCH
                    return []
                elif len(json_contents) == 1 and 'id' in json_contents[0]:
                    person = Person(json_contents[0]['sei'],json_contents[0]['seiyomi'],
                                    json_contents[0]['mei'],json_contents[0]['meiyomi'],
                                    json_contents[0]['id'],
                                    '')
                    await self.feedback(f'{person.seiyomi}{person.meiyomi}様ですね？',0)
                    personList.append(person)
            idx += 1

        # if personList==[]:
        #     await self.feedback("よく聞き取れませんでした。",0)
        #     self.error = INF_NOT_HEAR_WELL
        #     return []
        return personList

    async def interpret(self):
        print('AskName.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS: return []
        if (self.user.org=='genkikai' and self.user.role=='member' and not self.user.capability_sr):
            print(f'interpret> button action detected: {selection}')
            #["小川","小木曽","島田","久留","渡辺"]
            if selection == '1':
                person = Person('小川','オガワ','洋子','ヨウコ','M0047','')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？",0)
                return [person]
            elif selection == '2':
                person = Person('小木曾','オギソ','加代子','カヨコ','M0048','')
                await self.feedback(f'{person.seiyomi}{person.meiyomi}様ですね？',0)
                return [person]
            elif selection == '3':
                person = Person('今村','イマムラ','京子','キョウコ','M0027','')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？",0)
                return [person]
            elif selection=='4':
                person = Person('佐藤','サトウ','佳子','ヨシコ','M0098',"")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='5':
                person = Person('島田','シマダ','喜代子','キヨコ','M0103',"U9eaedcaf69309ebb504bcadc344fc910")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='6':
                person = Person('所','トコロ','美栄子','ミエコ','M0137',"U6b780e3bc04cb3fa7e868c73901d7531")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='7':
                person = Person('中越','ナカコシ','洋子','ヨウコ','M0141',"")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='8':
                person = Person('中島','ナカジマ','孝子','タカコ','M0142',"")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='9':
                person = Person('久留','ヒサトメ','正秀','マサヒデ','M0168',"Ue25373ca7df45fd53d6cdbe1cc592953")
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='10':
                person = Person('馬渕','マブチ','寿美子','スミコ','M0189','')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
            elif selection=='11':
                person = Person('渡辺','ワタナベ','美津子','ミツコ','M0227','')
                await self.feedback(f"{person.seiyomi}{person.meiyomi}様ですね？", 0)
                return [person]
        else:
            #if len(morphs)>0: await self.parse_name(morphs, self.person)
            return await self.parse_name(morphs)

class AskDate(Scene):
    def __init__(self, user, parent):
        super().__init__(user)
        self.parent = parent

    async def prompt(self):
        print('AskDate.prompt')
        if self.error == INF_NOT_HEAR_WELL:
            SPEECH = '何月何日と、ご指定下さい。'
            self.error = INF_RESET
        else:
            SPEECH = '日にちを、ご指定下さい。'
        TEXT = '日にち？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}"' + '}'
        await self.sendStr(jsonText)
        return
    
    def parse_month_day(self, morph1, morph2, day):
        if '月' == morph2['surface'] and 'pos' in morph1.keys() and morph1['pos'] == '名詞数***':
            day.month = morph1['surface']
        if '日' == morph2['surface'] and 'pos' in morph1.keys() and morph1['pos'] == '名詞数***':
            day.day = morph1['surface']

    async def parse_date(self, morphs):
        day = Day('','','','')
        for idx, val in enumerate(morphs):
            if idx > 0: self.parse_month_day(morphs[idx - 1], morphs[idx], day)
        if any(['今日' in m['surface'] for m in morphs]):
            today = datetime.today()
            day.day = today.day
        elif any(['明日' in m['surface'] for m in morphs]):
            tomorrow = datetime.today() + 1
            day.year = tomorrow.year
            day.month = tomorrow.month
            day.day = tomorrow.day + 1
        elif any(['昨日' in m['surface'] for m in morphs]):
            yesterday = datetime.today() - 1
            day.year = yesterday.year
            day.mopnth = yesterday.month
            day.day = yesterday.day
        if day.day != '':
            await self.feedback(f'{day.month}月{day.day}日ですね',0)
            return day
        else:
            return None

    async def interpret(self):
        print('askDate.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            return None
        else:
            if len(morphs)>0:
                return await self.parse_date(morphs)
            else:
                return None

class AskAmPm(Scene):
    def __init__(self, user, parent, day):
        super().__init__(user)
        self.parent = parent
        self.day = day

    async def prompt(self):
        print('AskAmPm.prompt')
        SPEECH = '午前午後を、ご指定下さい。'
        TEXT = '午前午後？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}"' + ',"suggestions":["午前","午後"]'+'}'
        await self.sendStr(jsonText)
        return
    
    async def parse_ampm(self,morphs,selection,dt):
        if any(['午前' in m['surface'] for m in morphs]) or selection=='1':
            dt.ampm = 'am'
            await self.feedback("午前ですね？",0)
        elif any(['午後' in m['surface'] for m in morphs]) or selection=='2':
            dt.ampm = 'pm'
            await self.feedback("午後ですね？",0)

    async def interpret(self):
        print('AskAmPm.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            return None
        else:
            await self.parse_ampm(morphs,selection,self.day)

class Reserve(Scene):

    def __init__(self, user, reserve):
        super().__init__(user)
        if reserve is None:
            self.reservation = Reservation()
        else:
            self.reservation = reserve
        self.operation = ''

    async def prompt(self):
        print('Reserve.prompt')
        self.error = INF_RESET
        if self.user.role == 'admin':
            SPEECH = '登録、削除、一覧表示、確認メッセージ送信のどれですか？'
            TEXT = '登録,削除,一覧,確認メッセ？'
            jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","suggestions":["登録","削除","一覧","確認メッセ","終了"]' + '}' #確認一斉送信を使う？
            await self.sendStr(jsonText)
            return

    async def interpret(self):
        print('Reserve.interpret')
        if self.counter > 5:
            await self.feedback("終了します",0)
            return None
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            await self.feedback("終了します", 1)
            return None
        if any(['登録' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("予約の登録を行います",0)
            self.operation = 'add'
            return UpdateReservation(self.user, self)
        elif any(['削除' in m['surface'] for m in morphs]) or selection == '2':
            self.operation = 'delete'
            await self.feedback("予約の削除を行います",0)
            return UpdateReservation(self.user, self)
        elif any(['一覧' in m['surface'] for m in morphs]) or selection == '3':
            await self.feedback("予約の一覧を表示します",2)
            return await self.actListReservation()
        elif any(['確認' in m['surface'] for m in morphs]) or any(['送信' in m['surface'] for m in morphs]) or \
            any(['メッセージ' in m['surface'] for m in morphs]) or selection == '4':
            await self.feedback("これから指定日の予約者に確認メッセージをLINEで送ります",0)
            return await self.actSendMessage()
        elif any(['終了' in m['surface'] for m in morphs]) or selection == '5':
            await self.feedback("終了します",2)
            return SeeYou(self.user)
        else:
            self.error = INF_NO_TARGET_WORDS
            await self.feedback("よく聞き取れませんでした",1)
            self.counter += 1
            return self

    async def actListReservation(self):
        print('actListReservation')
        await asyncio.sleep(2)
        URL = 'https://npogenkikai.net/reservations/'
        jsonText = '{' + f'"action":"goto_url","url":"{URL}"' + '}'
        print(jsonText)
        await self.sendStr(jsonText)
        return None

    async def actSendMessage(self):
        print('actSendMessage')
        self.reservation = Reservation()
        dt = AskDate(self.user, self)
        while self.reservation.date is None:
            self.reservation.date = await self.prompt_and_interpret(dt)
            if dt.error==ERR_TIMEOUT:
                await self.feedback("終了します", 0)
                return None
        ap = AskAmPm(self.user, self, self.reservation.date)
        while self.reservation.date.ampm=='':
            await self.prompt_and_interpret(ap)
            if ap.error==ERR_TIMEOUT:
                await self.feedback("終了します", 0)
                return None
        return SendReservationMessageS(self.user, self)

class UpdateReservation(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.parent = parent
        self.reservation = parent.reservation
        self.operation = parent.operation

    async def prompt(self):
        print('UpdateReservation.prompt')
        SPEECH = '予約を'
        TEXT = ''
        DISPLAY = ''
        if self.operation == "add":
            SPEECH += '追加する'
        else:
            SPEECH += '削除する'
        if self.reservation.date is None:
            SPEECH += '日にち、午前午後'
            TEXT += '日にち、午前午後'
        else:
            DISPLAY = f'{self.reservation.date.month}月{self.reservation.date.day}日{self.reservation.date.ampm}'
        if self.reservation.memberList==[]:
            SPEECH += '、氏名'
            if TEXT != '':
                TEXT += '、氏名'
            else:
                TEXT = '氏名'
        else:
            DISPLAY = ''
            for member in self.reservation.memberList:
                DISPLAY += f' {member.sei}{member.mei}様'
        SPEECH += 'をご指定ください。'
        TEXT += '？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","show":"{DISPLAY}"' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('UpdateReservation.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            await self.feedback("終了します", 1)
            return None

        if self.reservation.date is None:
            dt = AskDate(self.user, self)
            self.reservation.date = await dt.parse_date(morphs)
            while self.reservation.date is None:
                self.reservation.date = await self.prompt_and_interpret(dt)
                if dt.error == ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
        if self.reservation.date.ampm == '':
            ap = AskAmPm(self.user, self, self.reservation.date)
            await ap.parse_ampm(morphs,selection,self.reservation.date)
            while self.reservation.date.ampm == '':
                await self.prompt_and_interpret(ap)
                if ap.error == ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
        if self.reservation.memberList==[]:
            nm = AskName(self.user, self)
            self.reservation.memberList = await nm.parse_name(morphs)
            while self.reservation.memberList==[]:
                self.reservation.memberList = await self.prompt_and_interpret(nm)
                if nm.error == ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None

        return ConfirmReservation(self.user,self)

class ConfirmReservation(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.parent = parent
        self.reservation = parent.reservation
        self.operation = parent.operation

    async def prompt(self):
        print('ConfirmReservation.prompt')
        if self.operation=="add":
            SPEECH = '以下を追加しますか？'
            TEXT = '追加：'
        else:
            SPEECH = '以下を削除しますか？'
            TEXT = '削除：'
        TEXT += f'{self.reservation.date.month}月{self.reservation.date.day}日'
        if self.reservation.date.ampm =='am':
            TEXT += "午前"
        else:
            TEXT += "午後"
        #TEXT += f':{self.reservation.member.sei}{self.reservation.member.mei}様'
        for member in self.reservation.memberList:
            TEXT += f',{member.sei}{member.mei}様'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}", "suggestions":["はい","いいえ","日付修正","人名修正"]' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('ConfirmReservation.interpret')
        if self.counter > 5:
            await self.feedback("終了します",0)
            return None
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            await self.feedback("終了します", 1)
            return None

        if selection == '1' or any(['はい' in m['surface'] for m in morphs]):
            return await self.actUpdateReservation()
        elif selection == '2' or any(['いいえ' in m['surface'] for m in morphs]):
            await self.feedback("キャンセルします",0)
            return PostReservation(self.user, self)
        elif selection == '3' or any(['日付' in m['surface'] for m in morphs]):
            await self.feedback("戻ります",0)
            self.parent.reservation = Reservation()
            self.parent.reservation.memberList = self.reservation.memberList
            return self.parent
        elif selection == '4' or any(['人名' in m['surface'] for m in morphs]):
            await self.feedback("戻ります",0)
            self.parent.reservation = Reservation()
            self.parent.reservation.date = self.reservation.date
            return self.parent
        else:
            await self.feedback("よく聞き取れませんでした",1)
            self.counter += 1
            return self

    async def actUpdateReservation(self):
        print('actUpdateReservation')
        date = f'{self.reservation.date.year}/{self.reservation.date.month}/{self.reservation.date.day}'
        url = "https://npogenkikai.net/reserve.php"
        # json = {"command": self.operation,"id": self.reservation.member.id,"date": date,"ampm": self.reservation.date.ampm}
        idList = [m.id for m in self.reservation.memberList]
        json = {"command": self.operation,"ids": idList,"date": date,"ampm": self.reservation.date.ampm}
        print(f'{json}')
        th = threading.Thread(target=sendJson_sync, args=([url,json]))
        th.start()
        #return SendReservationMessage(self.user,self)
        return PostReservation(self.user, self)

class PostReservation(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.reservation = parent.reservation

    async def prompt(self):
        print('PostReservation.prompt')
        SPEECH = '同じ日時枠で予約作業を続けますか？'
        TEXT = '同じ時間枠？終了？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}"' + ',"suggestions":["同一時間枠","終了"]' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('PostReservation.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts!=SUCCESS:
            await self.feedback("終了します", 1)
            return None
        if any([m['surface'].startswith('同') for m in morphs]) or \
                any([m['surface'].startswith('続') for m in morphs]) or selection=='1':
            await self.feedback("同じ時間枠で予約管理を続けます",0)
            reservation = Reservation()
            reservation.date = self.reservation.date
            return Reserve(self.user, reservation)
        else:
            await self.feedback("終了します",1)
            return None


class SendReservationMessageS(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.reservation = parent.reservation
        self.idList = []

    async def prompt(self):
        print('SendReservationMessageS.prompt')
        self.error = INF_RESET
        SPEECH = '指定の時間枠の予約者です。よろしければ、全員にLINEで確認メッセージを送信します。'
        TEXT = '送信？'
        date = f'{self.reservation.date.year}/{self.reservation.date.month}/{self.reservation.date.day}'
        self.idList = await sendJson("https://npogenkikai.net/reserve.php",
                                          {"command": "listbytimeslot",
                                           "date": date,
                                           "ampm": self.reservation.date.ampm})
        list = f'{self.reservation.date.month}月{self.reservation.date.day}日{self.reservation.date.ampm}の予約:<br>'
        for r in self.idList:
            id = r['id']
            nameList = json.loads(pdNames[(pdNames['id'] == id)].to_json(orient="records", force_ascii=False))
            print(f'cache: {nameList}')
            if len(nameList) == 1:
                name = nameList[0]
            elif len(nameList) == 0:
                name = await sendJson("https://npogenkikai.net/id2name.php", {"id": id})
                print(f'id2name: {name}')
            nameStr = name['sei'] + name['mei']
            list += ' ' + nameStr
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","show":"{list}","suggestions":["送信","キャンセル"]' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('SendReservationMessageS.interpret')
        if self.counter > 5:
            await self.feedback("終了します",1)
            return None
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return None
        if any(['送信' in m['surface'] for m in morphs]) or selection=='1':
            await self.feedback("送信します",0)
            return await self.actSendMessage()
        elif any(['キャンセル' in m['surface'] for m in morphs]) or selection=='2':
            await self.feedback("送信をキャンセルします",0)
            return Reserve(self.user, None)
        else:
            self.error = INF_NO_TARGET_WORDS
            await self.feedback("よく聞き取れませんでした",1)
            self.counter += 1
            return self

    async def actSendMessage(self):
        print('actSendMessage')
        print(f'{self.idList}')
        sent = ''
        notsent = ''
        for r in self.idList:
            id = r['id']
            lineid = ''
            nameStr = ''
            json_contents = json.loads(pdNames[(pdNames['id'] == id)].to_json(orient="records", force_ascii=False))
            if len(json_contents) == 1:
                name = json_contents[0]
                nameStr = name['sei'] + name['mei']
                lineid = name['lineid']
            elif len(json_contents) == 0:
                #json_contents = await sendJson("https://npogenkikai.net/id2lineid.php",{"id":id})
                name = await sendJson("https://npogenkikai.net/id2name.php", {"id": id})
                nameStr = name['sei'] + name['mei']
                lineid = name['lineid']
            print(lineid, nameStr)
            if lineid != '':
                message = f'(試験運用です) {nameStr}様、'
                message += f'げんきかいの健康麻雀の、{self.reservation.date.month}月{self.reservation.date.day}日{self.reservation.date.ampm}の枠が予約されています。'
                message += 'なお、ホームページ https://npogenkikai.net/ から数週間後までの予約を随時確認できます。ただ、このリンクをLINEから開いても動かないので、やり方は担当者に聞いて下さい。'
                th = threading.Thread(target=sendToLine, args=([lineid, message]))
                th.start()
                print(message)
                sent += nameStr + ','
            else:
                #message = f'LINEのIDがわからないため、予約確認メッセージが送れません。{nameStr}さんのLINEIDを登録して下さい。'
                #th = threading.Thread(target=sendToLine, args=([None, message]))
                #th.start()
                #print(message)
                notsent += nameStr + ','
        # send a log to admin at once
        admin_message = '[管理者情報]\n' + sent + 'の方々に、『'\
            + f'(試験運用です) X様、'\
              + f'げんきかいの健康麻雀の、{self.reservation.date.month}月{self.reservation.date.day}日{self.reservation.date.ampm}の枠が予約されています。'\
                + 'なお、ホームページ https://npogenkikai.net/ から数週間後までの予約を随時確認できます。' + '』と送信されました。'
        admin_message += '\n次の方は、LINEIDが不明なため確認メッセージが送れませんでした：' + notsent
        th = threading.Thread(target=sendToLine, args=([None, admin_message]))
        th.start()
        print(admin_message)
        return Reserve(self.user, None)

class Record(Scene):

    def __init__(self, user, visit):
        super().__init__(user)
        if visit is None:
            self.visit = Visit()
        else:
            self.visit = visit
        self.operation = ''

    async def prompt(self):
        print('Record.prompt')
        self.error = INF_RESET
        if self.user.role == 'admin':
            SPEECH = '登録、削除、予約からのコピー、一覧表示のどれですか？'
            TEXT = '登録,削除,コピー,一覧？'
            jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","suggestions":["登録","削除","コピー","一覧","終了"]' + '}'  # 確認一斉送信を使う？
            await self.sendStr(jsonText)
            return

    async def interpret(self):
        print('cord.interpret')
        if self.counter > 5:
            await self.feedback("終了します", 0)
            return None
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return
        if any(['登録' in m['surface'] for m in morphs]) or selection == '1':
            await self.feedback("来場記録の登録を行います", 0)
            self.operation = 'add'
            return UpdateRecord(self.user, self)
        elif any(['削除' in m['surface'] for m in morphs]) or selection == '2':
            self.operation = 'delete'
            await self.feedback("来場記録の削除を行います", 0)
            return UpdateRecord(self.user, self)
        elif any(['コピー' in m['surface'] for m in morphs]) or selection == '3':
            await self.feedback("予約から来場記録へコピーします", 0)
            return Reservation2Record(self.user,self)
        elif any(['一覧' in m['surface'] for m in morphs]) or selection == '4':
            await self.feedback("来場記録の一覧を表示します", 2)
            return await self.actListRecord()
        elif any(['終了' in m['surface'] for m in morphs]) or selection == '5':
            await self.feedback("終了します", 2)
            return SeeYou(self.user)
        else:
            self.error = INF_NO_TARGET_WORDS
            await self.feedback("よく聞き取れませんでした", 1)
            self.counter += 1
            return self

    async def actListRecord(self):
        print('actListRecord')
        await asyncio.sleep(2)
        URL = 'https://npogenkikai.net/allrecords/'
        jsonText = '{' + f'"action":"goto_url","url":"{URL}"' + '}'
        print(jsonText)
        await self.sendStr(jsonText)
        return None

class Reservation2Record(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.user = user
        self.parent = parent

    async def prompt(self):
        print('Reservation2Record.prompt')
        SPEECH = 'コピーする日にちをご指定下さい。'
        TEXT = '日にち？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}"' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('Reservation2Record.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return None

        dt = AskDate(self.user, self)
        date = await dt.parse_date(morphs)
        while date is None:
            date = await self.prompt_and_interpret(dt)
            if dt.error == ERR_TIMEOUT:
                await self.feedback("終了します", 0)
                return None
        url = 'https://npogenkikai.net/reservation2record.php?date=' + f'{date.year}/{date.month}/{date.day}'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            respond = resp.read() # just ignore returned text
        #await sendGetRequest(url)
        await self.feedback("コピーしました", 0)
        return self.parent

class UpdateRecord(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.parent = parent
        self.visit = parent.visit
        self.operation = parent.operation

    async def prompt(self):
        print('UpdateRecord.prompt')
        SPEECH = '来場記録を'
        TEXT = ''
        DISPLAY = ''
        if self.operation == "add":
            SPEECH += '追加する'
        else:
            SPEECH += '削除する'
        if self.visit.date == None:
            SPEECH += '日にち'
            TEXT += '日にち'
        else:
            DISPLAY = f'{self.visit.date.month}月{self.visit.date.day}日'
        # if self.reservation.member.id == '':
        if self.visit.memberList == []:
            SPEECH += '、氏名'
            if TEXT != '':
                TEXT += '、氏名'
            else:
                TEXT = '氏名'
        else:
            DISPLAY = ''
            for member in self.visit.memberList:
                DISPLAY += f' {member.sei}{member.mei}様'
        SPEECH += 'をご指定ください。'
        TEXT += '？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}","show":"{DISPLAY}"' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('UpdateRecord.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return None

        if self.visit.date == None: # date maybe already filled
            dt = AskDate(self.user, self)
            self.visit.date = await dt.parse_date(morphs)
            while self.visit.date is None:
                self.visit.date = await self.prompt_and_interpret(dt)
                if dt.error == ERR_TIMEOUT:
                    await self.feedback("終了します", 0)
                    return None
        nm = AskName(self.user, self)
        self.visit.memberList = await nm.parse_name(morphs)
        while self.visit.memberList == []:
            self.visit.memberList = await self.prompt_and_interpret(nm)
            if nm.error == ERR_TIMEOUT:
                await self.feedback("終了します", 0)
                return None
            if self.error == ERR_TIMEOUT: return None

        return ConfirmRecord(self.user, self)


class ConfirmRecord(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.parent = parent
        self.visit = parent.visit
        self.operation = parent.operation

    async def prompt(self):
        print('ConfirmRecord.prompt')
        if self.operation == "add":
            SPEECH = '以下を追加しますか？'
            TEXT = '追加：'
        else:
            SPEECH = '以下を削除しますか？'
            TEXT = '削除：'
        TEXT += f'{self.visit.date.month}月{self.visit.date.day}日'
        for member in self.visit.memberList:
            TEXT += f',{member.sei}{member.mei}様'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}", "suggestions":["はい","いいえ","日付修正","人名修正"]' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('ConfirmRecord.interpret')

        if self.counter > 5:
            await self.feedback("終了します", 1)
            return None

        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return None

        if selection == '1' or any(['はい' in m['surface'] for m in morphs]):
            return await self.actUpdateRecord()
        elif selection == '2' or any(['いいえ' in m['surface'] for m in morphs]):
            await self.feedback("キャンセルします", 0)
            return PostRecord(self.user, self)
        elif selection == '3' or any(['日付' in m['surface'] for m in morphs]):
            await self.feedback("戻ります", 0)
            self.parent.visit = Visit()
            self.parent.visit.memberList = self.visit.memberList
            return self.parent
        elif selection == '4' or any(['人名' in m['surface'] for m in morphs]):
            await self.feedback("戻ります", 0)
            self.parent.visit = Visit()
            self.parent.visit.date = self.visit.date
            return self.parent
        else:
            await self.feedback("よく聞き取れませんでした", 1)
            self.counter += 1
            return self

    async def actUpdateRecord(self):
        print('actUpdateRecord')
        date = f'{self.visit.date.year}/{self.visit.date.month}/{self.visit.date.day}'
        url = "https://npogenkikai.net/record.php"
        # json = {"command": self.operation,"id": self.reservation.member.id,"date": date,"ampm": self.reservation.date.ampm}
        idList = [m.id for m in self.visit.memberList]
        json = {"command": self.operation, "ids": idList, "date": date}
        th = threading.Thread(target=sendJson_sync, args=([url, json]))
        th.start()
        return PostRecord(self.user, self)

class PostRecord(Scene):

    def __init__(self, user, parent):
        super().__init__(user)
        self.visit = parent.visit

    async def prompt(self):
        print('PostRecord.prompt')
        SPEECH = '同じ日時枠で来場記録作業を続けますか？'
        TEXT = '同じ時間枠？終了？'
        jsonText = '{' + f'"speech":"{SPEECH}","text":"{TEXT}"' + ',"suggestions":["同一時間枠","終了"]' + '}'
        await self.sendStr(jsonText)
        return

    async def interpret(self):
        print('PostRecord.interpret')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return None
        if any([m['surface'].startswith('同') for m in morphs]) or any(
                [m['surface'].startswith('続') for m in morphs]) or selection == '1':
            await self.feedback("同じ時間枠で来場記録管理を続けます", 0)
            visit = Visit()
            visit.date = self.visit.date
            return Record(self.user, visit)
        else:
            await self.feedback("終了します", 1)
            return None

class ViewInlineFrame(Scene):

    def __init__(self, user, url):
        super().__init__(user)
        self.url = url

    async def prompt(self):
        print('ViewInlineFrame.prompt')
        jsonText = '{' + f'"view":"{self.url}", suggestions":["戻る","終了"]' + '}'
        return

    async def interpret(self):
        print('ViewInlineFrame')
        sts, jsonDict, morphs, selection, intent = await self.decode_response()
        if sts != SUCCESS:
            await self.feedback("終了します", 1)
            return None
        if any([m['surface'].startswith('戻') for m in morphs]) or selection == 2:
            await self.feedback("戻ります", 0)
        else:
            await self.feedback("終了します", 1)
            return None

class SeeYou(Scene):
    async def prompt(self):
        print('SeeYou.prompt')
    async def interpret(self):
        print('SeeYou.interpret')
        SPEECH = 'またね'
        TEXT = 'またね'
        jsonText = '{' + f'"feedback":"{SPEECH}","text":"{TEXT}"'+'}'
        await self.sendStr(jsonText)
        await asyncio.sleep(2)
        #jsonText = '{' + f'"action":"finish"'+'}'
        #await self.sendStr(jsonText)
        return None

async def close_websockets():
    # clean up client
    if user.ws is not None and not user.ws.closed:
        await asyncio.sleep(1) # time to get 'finish' echo back log
        await user.ws.close()
    print('user.close_websockets > Websocket connections closed')

async def on_shutdown(app):
    print('on_shutdown >... ')
    await close_websockets()
    print('on_shutdown > app.cleanup')
    await app.cleanup()

def termination_handler(signal,frame):
    sys.exit(0)

if __name__ == '__main__':
    #
    # client must access with https://192.168.0.19:8081/www/index.html
    #
    print('user is up and running')

    signal.signal(signal.SIGINT, termination_handler)
    signal.signal(signal.SIGTERM, termination_handler)

    args = sys.argv
    user = User(args[1], args[2], args[3], args[4]) # userPort, org, role, invoker
    print(f'user port:{user.wsPort},org:{user.org},role:{user.role},invoker:{user.invoker}')

    tagger = MeCab.Tagger(r"-u ./user.dic")
    print(f'tagger type: {type(tagger)}')
    parsed = tagger.parse('私')  # preload dictionary
    user.tagger = tagger

    if user.invoker == 'rakudana_app':

        tokenizer = spm.SentencePieceProcessor()
        tokenizer.Load("./corpora/sentencepiece.model")

        wv = KeyedVectors.load('./intent_classifier/wv.model')

        szWV = 100
        numINTENT = 5
        intent_classifier = train.Net(szWV, numINTENT)  # .to(device)
        intent_classifier.load_state_dict(torch.load('./intent_classifier/intent_classifier.model'))

    line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
    line_parser = WebhookParser(config.LINE_CHANNEL_SECRET)

    app = None
    ctx = None
    if config.PROTOCOL=="http":
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

        app = aiohttp.web.Application(logger=logger)
        app.router.add_route('GET', '/ws', browser_handler)
        app.on_shutdown.append(on_shutdown)

        #threading.Thread(target=on_startup, args=([app])).start()

        if config.PROTOCOL=="http":
            aiohttp.web.run_app(app, host=config.HOST_INTERNAL_IP, port=user.wsPort)
        else:
            aiohttp.web.run_app(app, host=config.HOST_INTERNAL_IP, port=user.wsPort, ssl_context=ctx)

    except Exception as e:
        print('user.main > exception {}'.format(e))
        print(traceback.format_exc())

    finally:
        print('user.main > finally')
        history = [x.__class__.__name__ for x in user.dialog_history]
        print(f'>>>DIALOG HISTORY: {history}')
        #time.sleep(2) # for shutdown cor to execute
        #sys.exit(0)

