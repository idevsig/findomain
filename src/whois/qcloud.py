from __future__ import annotations

import logging

from deprecated import deprecated
from requests import Response
from type.domain import QueryResult
from utils.request import HttpRequest

from .whois_abc import WhoisABC


@deprecated(
    version="0.1.0",
    reason="腾讯云爬取数据功能已失效，推荐使用其自用 API：https://cloud.tencent.com/document/api/242/56203",
)
class Qcloud(WhoisABC):
    """
    腾讯云
    https://dnspod.cloud.tencent.com/cgi/capi?action=DescribeWhoisInfoSpecial&csrfCode=&innerCapiMark=1
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://dnspod.cloud.tencent.com"
        self.enable = False

    def _make_request_url(self):
        """
        生成请求的 URL
        """
        return f"{self.base_url}/cgi/capi/captcha?action=DescribeWhoisInfoSpecial&csrfCode=&innerCapiMark=1"

    def fetch(self, url, domain) -> Response:
        """
        请求数据
        :param url: 网址
        :param domain: 域名
        """

        payload_data = {
            "Version": "2018-08-08",
            "serviceType": "domain",
            "api": "DescribeWhoisInfoSpecial",
            "DomainName": domain,
            "dpNodeCustomClientIPField": "RealClientIp",
            "captchaCheckParam": "Refresh",
            "captchaTicket": "t03GFQYJTd-rRajUV7I6fXC39WXIz-h1yp86Wb0GMbPXprz5AzskQIC2OsJqKAUOgvUUkHL8JAgqV-_p6uEzbNCDijCG3EbqIvk2ua60DHnr9t6tPoEdQK-o3Uo7mRv9YeJ",
            "captchaRandstr": "@Dv2",
        }

        return (
            HttpRequest()
            .post(
                url,
                data=payload_data,
            )
            .response
        )

    def query(self, domain) -> QueryResult:
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
        response = self.fetch(self._make_request_url(), domain)
        logging.debug(f"{self.provider_name}, {response.text}")
        try:
            if response.status_code != 200:
                raise ValueError(f"status code is: {response.status_code}")

            resp = response.json()

            # 未注册
            if resp["code"] == "FailedOperation.DomainNotRegisterFailed":  # 未注册
                result.available = True
                result.error_code = 0
            elif resp["code"] == 0:  # 已注册
                result.available = False
                result.error_code = 0
                # 或者通过数据组成查询
                # result.available = resp['data']['Response']['WhoisInfo']['RegistrationDate'] == ''
            else:
                raise ValueError(
                    f"resp code {resp['code']}, message {resp['message']}",
                )

        #     # {"code":"99999999","message":"验证失败","error":{"name":"RequestError","message":"验证失败"},"timestamp":"2025-07-21T07:50:38.488Z","tid":"4b82c314be6582c709b0e7f8873eea61"}
        except Exception as e:
            raise ValueError(
                f"{self.provider_name} find domain: {domain}, err:{e}",
            )

        return result
