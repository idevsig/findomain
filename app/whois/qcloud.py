from ..utils.helpers import json_check
from ..utils.request import HttpRequest
from .whois import Whois


class Qcloud(Whois):
    '''
    腾讯云
    '''

    def __init__(self):
        self.name = self.__class__.__name__

        self.weburl = 'https://qcwss.cloud.tencent.com'

        self.suffixes = []

    def supported(self, suffixes):
        '''
        是否支持该后缀
        :param suffixes: 后缀
        '''
        if not self.suffixes:
            return True

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
        referer_url = 'https://whois.cloud.tencent.com/'
        req_url = '{}/domain/ajax/newdomain?action=CheckDomainAvailable&from=domain_buy'.format(
            self.weburl)
        return req_url

    def fetch(self, url, domain):
        '''
        请求数据
        :param url: 网址
        :param domain: 域名
        '''
        return HttpRequest().post(url, data={'DomainName': domain}).response

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

            resp = json_check(response)

            available = resp['result']['Available'] == True

            err = 0
        except Exception as e:
            print(f'Error: {self.name} find domain: {domain}, err:{e}')

        return available, regdate, expdate, err
