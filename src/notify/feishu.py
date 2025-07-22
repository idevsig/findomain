from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time

from utils.request import HttpRequest

from .notify_abc import NotifyABC


class Feishu(NotifyABC):
    """
    飞书通知推送类，支持加签认证发送文本消息
    """

    def __init__(self, token: str = '', secret: str = ''):
        self.token = token
        self.secret = secret
        self._http = HttpRequest().update_headers(
            {
                'Content-Type': 'application/json',
            },
        )

    def _generate_signature(self) -> tuple[str, str]:
        """
        生成 timestamp 与 sign，用于请求验证
        :return: (timestamp, signature)
        """
        timestamp = str(int(time.time()))
        sign_str = f'{timestamp}\n{self.secret}'.encode()
        hmac_code = hmac.new(sign_str, b'', digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, signature

    def _build_url(self, timestamp: str = '', sign: str = '') -> str:
        return f'https://open.feishu.cn/open-apis/bot/v2/hook/{self.token}'

    def send(self, message: str):
        """
        发送飞书文本通知
        :param message: 文本内容
        """
        if not self.token:
            logging.warning(
                f'{self.provider_name} 机器人 token 未设置，跳过发送',
            )
            return

        logging.info(f'准备通过 - {self.provider_name} 机器人 - 推送消息...')

        data = {
            'msg_type': 'text',
            'content': {
                'text': message,
            },
        }

        if self.secret:
            timestamp, sign = self._generate_signature()
            data.update(
                {
                    'timestamp': timestamp,
                    'sign': sign,
                },
            )

        try:
            self._http.post(self._build_url(), json=data)
            logging.info(f'{self.provider_name} 消息发送成功')
            return self._http.response
        except Exception as e:
            logging.error(f'{self.provider_name} 消息发送失败', exc_info=e)
