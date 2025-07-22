from __future__ import annotations

import logging
import random

from type.domain import QueryResult
from utils.request import HttpRequest
from utils.util import remove_url
from whois.whois_abc import WhoisABC


class West(WhoisABC):
    """
    西部数码
    """

    def __init__(self):
        super().__init__()
        self.base_urls = [
            'https://www.west.xyz',
            'https://www.363.hk',
            'https://www.west.cn',
        ]
        # self.enable = False

    def _make_request_url(self, domain):
        """
        生成请求的 URL
        :param domain: 域名
        """
        return f'{self.base_url}/web/whois/whoisinfo?domain={domain}&server=&refresh=0'

    def fetch(self, url):
        """
        请求数据
        :param url: 网址
        """
        return HttpRequest().get(url).response

    def query(self, domain):
        """
        查询域名
        :param domain: 域名
        """
        self.base_url = random.choice(self.base_urls)
        self._is_service_available()

        result = QueryResult(
            domain=domain,
            available=False,
            status='',
            registration_date='',
            expiration_date='',
            nameserver='',
            icpInfo='',
            error_code=1,
            provider=self.provider_name,
        )
        # response = self.fetch(self._make_request_url(domain))
        response = self.fetch(
            'https://fileserver.zzzzy.com/public/findomain_test_noba.json'
        )
        try:
            # print(response.text)
            if response.status_code != 200:
                raise ValueError(f'status code {response.status_code}')

            resp = response.json()
            logging.debug(f'{self.provider_name}, {resp}')
            # code 为 200 时，表示已被注册
            # code 为 100 时，表示未被注册或注册局保留
            # 保险起见，使用注册日期字段判断是否已被注册
            if resp['code'] == 200 or resp['code'] == 100:
                # 根据注册时间判断
                result.available = resp['regdate'] == ''
                if not result.available:
                    result.registration_date = resp['regdate']
                    result.expiration_date = resp['expdate']
                result.error_code = 0

                if resp['status']:
                    result.status = remove_url(resp['status']).strip()
                if resp['nameserver']:
                    # 只取第一个
                    result.nameserver = resp['nameserver'].split(',')[0]
                if resp['icpInfo']:
                    result.icpInfo = resp['icpInfo'].get('Ztbah', '')
            else:
                raise ValueError(
                    f'resp code {resp["code"]}, message {resp["dom_em"]}',
                )
        except Exception as e:
            raise ValueError(
                f'find domain: {domain}, err:{e}',
            )

        return result
