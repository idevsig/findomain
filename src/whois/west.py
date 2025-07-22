from __future__ import annotations

import logging
import random

from type.domain import QueryResult
from utils.request import HttpRequest
from whois.whois_abc import WhoisABC


class West(WhoisABC):
    """
    西部数码
    """

    def __init__(self):
        super().__init__()
        self.base_urls = [
            "https://www.west.xyz",
            "https://www.363.hk",
            "https://west.cn",
        ]
        self.base_url = random.choice(self.base_urls)
        # self.enable = False

    def _make_request_url(self, domain):
        """
        生成请求的 URL
        :param domain: 域名
        """
        return f"{self.base_url}/web/whois/whoisinfo?domain={domain}&server=&refresh=0"

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
        self._is_service_available()

        result = QueryResult(
            domain=domain,
            available=False,
            registration_date="",
            expiration_date="",
            error_code=1,
            provider=self.provider_name,
        )
        response = self.fetch(self._make_request_url(domain))
        logging.debug(f"{self.provider_name}, {response.text}")
        try:
            # print(response.text)
            if response.status_code != 200:
                raise ValueError(f"status code {response.status_code}")

            resp = response.json()
            # code 为 200 时，表示已被注册
            # code 为 100 时，表示未被注册或注册局保留
            # 保险起见，使用注册日期字段判断是否已被注册
            if resp["code"] == 200 or resp["code"] == 100:
                # 根据注册时间判断
                result.available = resp["regdate"] == ""
                if not result.available:
                    result.registration_date = resp["regdate"]
                    result.expiration_date = resp["expdate"]
                result.error_code = 0
            else:
                raise ValueError(
                    f"resp code {resp['code']}, message {resp['dom_em']}",
                )
        except Exception as e:
            raise ValueError(
                f"Error: {self.name} find domain: {domain}, err:{e}",
            )

        return result
