import random
import re
from ..utils.request import HttpRequest
from .whois import Whois


class Zzidc(Whois):
    '''
    景安网络
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

    def supported(self, suffixes):
        '''
        是否支持该后缀
        :param suffixes: 后缀
        '''
        try:
            self.suffixes.index(suffixes)
            return True
        except Exception as e:
            print(
                f'Error: ({self.name}) this suffix is not supported: {suffixes}')
            return False

    def requrl(self):
        '''
        生成请求的 URL
        '''
        isp_url = random.choice(self.weburls)

        referer_url = 'https://www.zzidc.com'
        req_url = '{}/domain/checkDomain'.format(
            isp_url)
        return req_url

    def fetch(self, url, domain):
        '''
        请求数据
        :param url: 网址
        '''
        return HttpRequest().post(url, data={'domain': domain}).response

    def available(self, domain):
        '''
        是否可注册
        :param domain: 域名
        '''
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
