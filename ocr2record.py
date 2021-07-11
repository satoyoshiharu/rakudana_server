import MeCab
import sys
import re
import urllib.request
import json

async def sendJson(url, data):
    print(f'sendJson > {url}, {data}')
    headers = {'Content-Type': 'application/json_string'}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        print('respose: ', res)
        json_contents = json.load(res)
        print('json_string contents', json_contents)
        return json_contents

async def sendGetRequest(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        respond = resp.read()
        jsonDict = json.loads(respond)
        print(f'received: {jsonDict}')
        return jsonDict

def ocr2record(text):

    #tagger = MeCab.Tagger(r"-d /home/ysato/.local/lib/python3.8/site-packages/unidic_lite/dicdir -u ./user.dic")
    #tagger = MeCab.Tagger(r"-d /usr/share/mecab/dic/ipadic -u ./user.dic")
    #tagger = MeCab.Tagger(r"-u ./user.dic")
    tagger = MeCab.Tagger()
    parsed = tagger.parse(text)
    print(parsed)
    morphs = []
    for token in parsed.split('\n'):
        attr = re.split('[\t,]', token)
        print(attr)
        if len(attr) > 1:
            morph = {'surface': attr[0], 'base': attr[8], 'pos': attr[4]}
        else:
            morph = {'surface': attr[0]}
        morphs.append(morph)
    print(morphs)
    for i in range(len(morphs)-1):
        if i<len(morphs)-1 and morphs[i]['pos']=='姓' and morphs[i+1]['pos']=='名':
            sei = morphs[i]['surface']
            mei = morphs[i+1]['surface']
            json_contents = sendJson("https://npogenkikai.net/name2id.php", {"sei": sei, "mei": mei})
            print(f'name2id returns: {json_contents}')
            if json_contents == '' or 'error' in json_contents[0]:
                print('error', json_contents['error'])
                print(f'{sei}{mei} not found')
                id = ''
            elif len(json_contents) > 0 and 'userid' in json_contents[0]:
                id = json_contents[0]['userid']
            if id!='':
                json_contents = sendGetRequest("https://npogenkikai.net/join.php?reg=app" + "&userid=" + id)
                if 'success' in json_contents[0]:
                    print(f'success: {id}')
                else:
                    print(f'failed: {id}')

if __name__ == '__main__':
    #args = sys.argv
    #text = args[1]
    # test
    text = '小川洋子相沢京子加藤久美子中根文子'
    #text = 'オガワヨウコアイザワキョウコカトウクミコナカネフミコ'
    ocr2record(text)