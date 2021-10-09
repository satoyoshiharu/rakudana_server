# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage, FollowEvent, SourceUser, JoinEvent, MemberJoinedEvent, ImageSendMessage
)
import ssl
import config
import line_config
import subprocess
import shlex
import datetime
import ocr

app = Flask(__name__)

line_bot_api = LineBotApi(line_config.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(line_config.LINE_CHANNEL_SECRET)

def log(str):
    app.logger.info(str)
    print(str)

@app.route("/line", methods=['POST'])
def line():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:

        app.logger.info(f'event: {event}')
        print(f'{event}')

        if isinstance(event.source, SourceUser):
            log("userId: " + event.source.user_id)
            userId = event.source.user_id
            profile = line_bot_api.get_profile(userId)
            line_bot_api.push_message(line_config.LINE_ADMIN_USERID, TextSendMessage(text=f"{profile.display_name}さんのLINE-ID：{userId}"))
            line_bot_api.push_message(line_config.LINE_ADMIN2_USERID, TextSendMessage(text=f"{profile.display_name}さんのLINE-ID：{userId}"))
            line_bot_api.push_message(line_config.LINE_ADMIN3_USERID, TextSendMessage(text=f"{profile.display_name}さんのLINE-ID：{userId}"))
            #TODO: check whther I need to add new entry or already existing one????

        if isinstance(event, FollowEvent) or isinstance(event, JoinEvent) or isinstance(event, MemberJoinedEvent):
            log("userId: " + event.source.user_id)
            userId = event.source.user_id
            profile = line_bot_api.get_profile(userId)
            line_bot_api.push_message(line_config.LINE_ADMIN_USERID, TextSendMessage(text=f"{profile.display_name}さんのLINE-ID：{userId}"))
            line_bot_api.push_message(line_config.LINE_ADMIN2_USERID, TextSendMessage(text=f"{profile.display_name}さんのLINE-ID：{userId}"))
            line_bot_api.push_message(line_config.LINE_ADMIN3_USERID, TextSendMessage(text=f"{profile.display_name}さんのLINE-ID：{userId}"))

        #jpg memo handling to register join records

        if isinstance(event, MessageEvent) and isinstance(event.message, ImageMessage):
            message_content = line_bot_api.get_message_content(event.message.id)
            # use unique name to work around line uses cache to forward the image
            now = datetime.datetime.now()
            image_file_name = now.strftime('%Y%m%d%-H%M%S')
            with open(config.WORKING_DIR + 'record/' + image_file_name + '.jpg', "wb") as f:
                for chunk in message_content.iter_content():
                    f.write(chunk)
            # forward to administrator
            line_bot_api.push_message(line_config.LINE_ADMIN_USERID,
                                      ImageSendMessage(
                                          original_content_url='https://rakudana.com:8080/record/' + image_file_name + '.jpg',
                                          preview_image_url='https://rakudana.com:8080/record/' + image_file_name + '.jpg'
                                      ))
            line_bot_api.push_message(line_config.LINE_ADMIN2_USERID,
                                      ImageSendMessage(
                                          original_content_url='https://rakudana.com:8080/record/' + image_file_name + '.jpg',
                                          preview_image_url='https://rakudana.com:8080/record/' + image_file_name + '.jpg'
                                      ))
            # kick HWR
            #subprocess.Popen(shlex.split(f'python3 {config.WORKING_DIR}ocr.py {config.WORKING_DIR}record/{image_file_name}'))
            log("image: " + image_file_name)
            ocr.ocr(image_file_name)

        # forward to admin
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            log(f"{profile.display_name}さんから：{event.message.text}")
            line_bot_api.push_message(line_config.LINE_ADMIN_USERID,
                                      TextSendMessage(text=f"{profile.display_name}さんから：{event.message.text}"))
            line_bot_api.push_message(line_config.LINE_ADMIN2_USERID,
                                      TextSendMessage(text=f"{profile.display_name}さんから：{event.message.text}"))
            line_bot_api.push_message(line_config.LINE_ADMIN3_USERID,
                                      TextSendMessage(text=f"{profile.display_name}さんから：{event.message.text}"))
            #echo back
            #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('/etc/letsencrypt/live/rakudana.com/fullchain.pem',
                        keyfile='/etc/letsencrypt/live/rakudana.com/privkey.pem')

    app.run(host='0.0.0.0', debug=options.debug, port=options.port, ssl_context=context)