import random
import re

from ..utils.request import HttpRequest
from .whois import Whois

'''
景安网络
'''


class Zzidc(Whois):
    '''
    初始化
    '''

    def __init__(self):
        self.name = self.__class__.__name__

        self.weburls = ['https://www.zzidc.com', 'https://www.zzidc.hk']

        self.suffixes = [
            'net',
            'com',
            'cn',
            'cc',
            'top',
            'wang',
            'vip',
            'xyz',
        ]
        pass

    '''
    是否支持该后缀
    '''

    def supported(self, suffixes):
        try:
            self.suffixes.index(suffixes)
            return True
        except Exception as e:
            print(
                f'Error: ({self.name}) this suffix is not supported: {suffixes}')
            return False

    '''
    生成请求的 URL
    '''

    def requrl(self):
        isp_idx = random.randint(0, len(self.weburls) - 1)
        isp_url = self.weburls[isp_idx]

        referer_url = 'https://www.zzidc.com'
        req_url = '{}/domain/checkDomain'.format(
            isp_url)
        return req_url

    '''
    请求数据
    '''

    def fetch(self, url, domain):
        return HttpRequest().post(url, data={'domain': domain})

    '''
    是否可注册
    '''

    def available(self, domain):
        req_url = self.requrl()
        response = self.fetch(req_url, domain)

        available, regdate, expdate, err = False, '', '', 1
        try:
            # print(response.text)
            if response.status_code != 200:
                raise ValueError(f'status code is: {response.status_code}')

            date_pattern = r'val:\s*(\d+)'

            val_match = re.search(date_pattern, response.text)
            if val_match:
                available = val_match.group(1) == '1'

            err = 0
        except Exception as e:
            print(f'Error: {self.name} find domain: {domain}, err:{e}')

        return available, regdate, expdate, err
