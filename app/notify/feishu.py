import json
import time
import hmac
import hashlib
import base64
from urllib import parse

from ..utils.request import HttpRequest
from .notify import Notify

'''
飞书通知
'''


class Feishu(Notify):
    def __init__(self, token='', secret=''):
        self.token = token
        self.secret = secret

    '''
    签名
    '''

    def signature(self):
        timestamp = str(round(time.time()))
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode(
            "utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        # print(timestamp)
        # print(sign)
        return (timestamp, sign)

    '''
    生成请求的 URL
    '''

    def requrl(self):
        return 'https://open.feishu.cn/open-apis/bot/v2/hook/{}'.format(
            self.token)

    '''
    发送通知
    '''

    def send(self, message):
        if not self.token or not self.secret:
            print(f'未检测到 "飞书机器人"')
            return

        print(f'检测到 "飞书机器人" 准备推送消息')

        timestamp, sign = self.signature()
        req_url = self.requrl()

        headers = {
            'content-type': 'application/json',
        }
        req = HttpRequest()
        req.update_headers(headers)

        data = {
            'timestamp': timestamp,
            'sign': sign,
            'msg_type': "text",
            'content': {
                'text': message
            }
        }
        data = json.dumps(data, indent=4)

        response = req.post(req_url, data=data.encode('utf-8'))

        # print(self.token, self.secret)
        print(message)
        print(req_url)
        # print(response)
        print(response.json())
        return response
