import config
import json
import urllib.request
import logging
import re
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent, SourceUser
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import re
import names

DEBUG = True

def sendJson(url,data):
    print(f'sendJson > {url}, {data}')
    headers = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        print('respose: ', res)
        json_contents = json.load(res)
        print('json contents', json_contents)
        return json_contents

def sendToLine(lineid, message):
    if lineid != None:
        line_bot_api.push_message(lineid, TextSendMessage(text=message))
        print(f'sent to {lineid}: {message}')
    else:
        line_bot_api.push_message(config.LINE_ADMIN_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(config.LINE_ADMIN2_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(config.LINE_ADMIN3_USERID, TextSendMessage(text=message))
        line_bot_api.push_message(config.LINE_ADMIN4_USERID, TextSendMessage(text=message))

pdNames = pd.DataFrame(data=names.names, columns=["id","sei","seiyomi","mei","meiyomi","lineid"])

if __name__ == '__main__':
    line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
    line_parser = WebhookParser(config.LINE_CHANNEL_SECRET)

    today = datetime.today()
    #
    # copy today's reservation data to record table
    #
    url = 'https://npogenkikai.net/reservation2record.php?date=' + f'{today.year}/{today.month}/{today.day}'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        respond = resp.read()  # just ignore returned text
    #
    # send confirmation of the same day of next week
    #

    cfm = today + relativedelta(days=7)
    date = f'{cfm.year}/{cfm.month}/{cfm.day}'
    print(f'{cfm}')
    idList = sendJson("https://npogenkikai.net/reserve.php",
                            {"command": "listbytimeslot", "date": date, "ampm": "pm"})
    print(f'idLIst: {idList}')
    if len(idList) == 0: exit(0)

    sent = ''
    notsent = ''
    for r in idList:
        id = r['id']
        lineid = ''
        nameStr = ''
        json_contents = json.loads(pdNames[(pdNames['id'] == id)].to_json(orient="records", force_ascii=False))
        if len(json_contents) == 1:
            name = json_contents[0]
            nameStr = name['sei'] + name['mei']
            lineid = name['lineid']
        elif len(json_contents) == 0:
            name = sendJson("https://npogenkikai.net/id2name.php", {"id": id})
            nameStr = name['sei'] + name['mei']
            lineid = name['lineid']
        print(lineid, nameStr)
        if lineid != '':
            message = f'(試験運用です) {nameStr}様、'
            message += f'げんきかいの健康麻雀の、{cfm.month}月{cfm.day}日pmの枠が予約されています。'
            message += 'なお、ホームページ https://npogenkikai.net/ から数週間後までの予約を随時確認できます。'
            sendToLine(lineid, message)
            sent += nameStr + ','
        else:
            notsent += nameStr + ','
    admin_message = '[管理者情報]\n次の方に確認メッセージが送信されました：\n' + sent + '\n『'\
        + f'(試験運用です) X様、'\
          + f'げんきかいの健康麻雀の、{cfm.month}月{cfm.day}日pmの枠が予約されています。'\
            + 'なお、ホームページ https://npogenkikai.net/ から数週間後までの予約を随時確認できます。' + '』'
    admin_message += '\n次の方は、LINEIDが不明なため確認メッセージが送れませんでした：\n' + notsent
    sendToLine(None,admin_message)
    print(admin_message)
