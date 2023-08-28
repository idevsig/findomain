import random

from ..utils.helpers import json_check
from ..utils.request import HttpRequest
from .whois import Whois

'''
西部数码
'''


class West(Whois):
    '''
    初始化
    '''

    def __init__(self):
        self.name = self.__class__.__name__

        self.weburls = ['https://www.west.xyz',
                        'https://www.363.hk', 'https://west.cn']

        self.suffixes = []

    '''
    是否支持该后缀
    '''

    def supported(self, suffixes):
        if not self.suffixes:
            return True

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

    def requrl(self, domain):
        isp_idx = random.randint(0, len(self.weburls) - 1)
        isp_url = self.weburls[isp_idx]

        referer_url = '{}/web/whois/whois'.format(isp_url)
        # https://www.west.xyz/en/domain/whois.asp
        req_url = '{}/web/whois/whoisinfo?domain={}&server=&refresh=0'.format(
            isp_url, domain)
        return req_url

    '''
    请求数据
    '''

    def fetch(self, url):
        return HttpRequest().get(url)

    '''
    是否可注册
    '''

    def available(self, domain):
        req_url = self.requrl(domain)
        response = self.fetch(req_url)

        available, regdate, expdate, err = False, '', '', 1
        try:
            # print(response.text)
            if response.status_code != 200:
                raise ValueError(f'status code is: {response.status_code}')

            resp = json_check(response)

            if resp['code'] == 200 or resp['code'] == 100:
                available = resp['regdate'] == ''

                if not available:
                    regdate = resp['regdate']
                    expdate = resp['expdate']

            err = 0
        except Exception as e:
            print(f'Error: {self.name} find domain: {domain}, err:{e}')

        return available, regdate, expdate, err