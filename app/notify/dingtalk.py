import time
import hmac
import hashlib
import base64
from urllib import parse

from ..utils.request import HttpRequest
from .notify import Notify

'''
钉钉通知
'''


class Dingtalk(Notify):
    def __init__(self, token='', secret=''):
        self.token = token
        self.secret = secret

    '''
    签名
    '''

    def signature(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc,
                             digestmod=hashlib.sha256).digest()
        sign = parse.quote_plus(base64.b64encode(hmac_code))
        # print(timestamp)
        # print(sign)
        return (timestamp, sign)

    '''
    生成请求的 URL
    '''

    def requrl(self, sign):
        return 'https://oapi.dingtalk.com/robot/send?access_token={}{}'.format(
            self.token, sign)

    '''
    发送通知
    '''

    def send(self, message):
        if not self.token or not self.secret:
            print(f'未检测到 "钉钉机器人"')
            return

        print(f'检测到 "钉钉机器人" 准备推送消息')

        timestamp, sign = self.signature()
        req_url = self.requrl(f'&timestamp={timestamp}&sign={sign}')

        headers = {
            'content-type': 'application/json',
        }
        req = HttpRequest()
        req.update_headers(headers)

        data = '{"msgtype": "text","text": {"content":"' + message + '"}}'
        req.post(req_url, data=data.encode('utf-8'))

        # print(self.token, self.secret)
        print(message)
        print(req_url)
        # print(response)
        print(req.json)
        return req.response
