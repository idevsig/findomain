from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time
from urllib.parse import quote_plus

from utils.request import HttpRequest

from .notify_abc import NotifyABC


class Dingtalk(NotifyABC):
    """
    钉钉通知推送类，支持带签名的加密消息发送
    """

    def __init__(self, token: str = "", secret: str = ""):
        self.token = token
        self.secret = secret
        self._http = HttpRequest().update_headers(
            {
                "Content-Type": "application/json",
            },
        )

    def _generate_signature(self) -> tuple[str, str]:
        """
        生成签名时间戳和签名字符串
        :return: (timestamp, signature)
        """
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature = quote_plus(base64.b64encode(hmac_code))
        return timestamp, signature

    def _build_url(self, timestamp: str = "", sign: str = "") -> str:
        """
        构建完整请求 URL
        """
        return (
            f"https://oapi.dingtalk.com/robot/send?"
            f"access_token={self.token}&timestamp={timestamp}&sign={sign}"
        )

    def send(self, message: str):
        """
        发送钉钉通知消息
        :param message: 要发送的文本内容
        """
        if not self.token or not self.secret:
            logging.warning(
                f"{self.provider_name} 机器人 token 或 secret 未配置，取消发送。",
            )
            return

        logging.info(f"准备通过 - {self.provider_name} 机器人 - 推送消息...")

        try:
            timestamp, sign = self._generate_signature()
            url = self._build_url(timestamp, sign)
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message,
                },
            }

            self._http.post(url, json=payload)
            logging.info(f"{self.provider_name} 消息发送成功")
            return self._http.response

        except Exception as e:
            logging.error(f"{self.provider_name} 消息发送失败", exc_info=e)
