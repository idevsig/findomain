import re

from ..utils.helpers import json_check
from ..utils.request import HttpRequest
from .whois import Whois

'''
Rapidapi
https://rapidapi.com/backend_box/api/bulk-whois/
33 / day | Hard Limit
'''


class Rapidapi(Whois):
    '''
    初始化
    '''

    def __init__(self):
        self.name = self.__class__.__name__

        self.weburl = 'https://pointsdb-bulk-whois-v1.p.rapidapi.com'

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
        req_url = '{}/whois'.format(
            self.weburl)
        return req_url

    '''
    请求数据
    '''

    def fetch(self, url, domain):
        querystring = {"domains": domain, "format": "split"}
        headers = {
            'x-rapidapi-host': "pointsdb-bulk-whois-v1.p.rapidapi.com",
            'x-rapidapi-key': "e7cc80a32emsh3af8115155e1edcp11b416jsnbe22a2f028d0"
        }
        req = HttpRequest()
        req.update_headers(headers)
        return req.get(url, params=querystring).response

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

            date_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'

            info = resp[domain]
            if 'No match' in info[0]['0']:
                available = True
            else:
                # 提取日期
                for i in info:
                    for _, item in i.items():
                        # 创建时间
                        if not regdate and 'Creation Date:' in item:
                            regdate = re.findall(date_pattern, item)[0]
                        # 过期时间
                        elif not expdate and 'Registry Expiry Date:' in item:
                            expdate = re.findall(date_pattern, item)[0]

                    # 日期提取完成
                    if regdate and expdate:
                        break

            err = 0
        except Exception as e:
            print(f'Error: Rapidapi find domain: {domain}, err:{e}')

        return available, regdate, expdate, err
