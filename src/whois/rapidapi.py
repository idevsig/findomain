import logging
import re

from type.domain import QueryResult
from utils.request import HttpRequest
from whois.whois_abc import WhoisABC


class Rapidapi(WhoisABC):
    '''
    Rapidapi
    https://rapidapi.com/backend_box/api/bulk-whois/
    33 / day | Hard Limit
    '''

    def __init__(self):
        super().__init__()
        self.base_url = 'https://pointsdb-bulk-whois-v1.p.rapidapi.com'
        self.enable = False # 限制太多，不建议使用
        self.apk_key = 'e7cc80a32emsh3af8115155e1edcp11b416jsnbe22a2f028d0'

    def _make_request_url(self):
        '''
        生成请求的 URL
        '''
        return f'{self.base_url}/whois'

    def fetch(self, url, domain):
        '''
        请求数据
        :param url: 网址
        :param domain: 域名
        '''
        querystring = {"domains": domain, "format": "split"}
        headers = {
            'x-rapidapi-host': self.base_host,
            'x-rapidapi-key': self.apk_key,
        }
        return HttpRequest().update_headers(headers).get(url, params=querystring).response

    def query(self, domain):
        '''
        查询域名
        :param domain: 域名
        '''
        self._is_service_available()
        
        result = QueryResult(
            domain=domain,
            available=False,
            registration_date='',
            expiration_date='',
            error_code=1,
            provider=self.provider_name
        )     
        response = self.fetch(self._make_request_url(), domain)
        logging.debug(f'{self.provider_name}, {response.text}')
        try:
            # print(response.text)
            if response.status_code != 200:
                raise ValueError(f'status code {response.status_code}')

            resp = response.json()
            result.error_code = 0
            date_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'
            info = resp[domain]
            if 'does not exist' in info[0]['0']:
                result.available = True
            else:
                # 提取日期
                for i in info:
                    for _, item in i.items():
                        # 创建时间
                        if not result.registration_date and 'Creation Date:' in item:
                            result.registration_date = re.findall(date_pattern, item)[0]
                        # 过期时间
                        elif not result.expiration_date and 'Registry Expiry Date:' in item:
                            result.expiration_date = re.findall(date_pattern, item)[0]

                    # 日期提取完成
                    if result.registration_date and result.expiration_date:
                        break
        except Exception as e:
            raise ValueError(f'Error: Rapidapi find domain: {domain}, err:{e}')

        return result
