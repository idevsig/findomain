from ..utils.helpers import json_check
from ..utils.request import HttpRequest
from .whois import Whois

'''
腾讯云
'''


class Qcloud(Whois):
    '''
    初始化
    '''

    def __init__(self):
        self.name = self.__class__.__name__

        self.weburl = 'https://qcwss.cloud.tencent.com'

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

    def requrl(self):
        referer_url = 'https://whois.cloud.tencent.com/'
        req_url = '{}/domain/ajax/newdomain?action=CheckDomainAvailable&from=domain_buy'.format(
            self.weburl)
        return req_url

    '''
    请求数据
    '''

    def fetch(self, url, domain):
        return HttpRequest().post(url, data={'DomainName': domain}).response

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

            resp = json_check(response)

            available = resp['result']['Available'] == True

            err = 0
        except Exception as e:
            print(f'Error: {self.name} find domain: {domain}, err:{e}')

        return available, regdate, expdate, err
