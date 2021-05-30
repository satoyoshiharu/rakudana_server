'''
 UI, Communication controller
 Process per user
'''
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

def sendToLine(lineid, message):
    line_bot_api.push_message(lineid, TextSendMessage(text=message))
    print(f'sent to {lineid}: {message}')

if __name__ == '__main__':
    line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
    line_parser = WebhookParser(config.LINE_CHANNEL_SECRET)
    lineid = 'Ua93b46fa3939ef58c7786878f9b70abc'
    message = 'げんきかいのスタッフです。中越様のLINEで間違いないでしょうか？　お名前の読みはげんきかいの名簿だ「ようこ」ですが「ひろこ」の間違いでしょうか、ご確認お願いいたします。'