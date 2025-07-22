from __future__ import annotations

import logging
import random
import re

from type.domain import QueryResult
from utils.request import HttpRequest
from whois.whois_abc import WhoisABC


class Zzidc(WhoisABC):
    """
    景安网络
    """

    def __init__(self):
        super().__init__()
        self.base_urls = [
            'https://www.zzidc.com',
            # 'https://www.zzidc.hk',
        ]
        self.supported_suffixes = [
            'net',
            'com',
            'cn',
            'cc',
            'top',
            'wang',
            'vip',
            'xyz',
        ]
        # self.enable = False

    def _make_request_url(self):
        """
        生成请求的 URL
        """
        return f'{self.base_url}/domain/checkDomain'

    def fetch(self, url, domain):
        """请求数据"""
        # 对于SSL问题，尝试禁用SSL验证
        return HttpRequest().post(url, data={'domain': domain}).response

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
            error_code=1,
            provider=self.provider_name,
        )
        response = self.fetch(self._make_request_url(), domain)
        logging.debug(f'{self.provider_name}, {response.text}')
        try:
            # print(response.text)
            if response.status_code != 200:
                raise ValueError(f'status code {response.status_code}')

            date_pattern = r'val:\s*(\d+)'
            val_match = re.search(date_pattern, response.text)
            if val_match:
                result.available = val_match.group(1) == '1'

            result.error_code = 0
        except Exception as e:
            raise ValueError(
                f'Error: {self.name} find domain: {domain}, err:{e}',
            )

        return result
