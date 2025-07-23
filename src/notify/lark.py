from __future__ import annotations

from notify.feishu import Feishu


class Lark(Feishu):
    """
    飞书通知推送类，支持加签认证发送文本消息
    """

    def _build_url(self) -> str:
        return f'https://open.larksuite.com/open-apis/bot/v2/hook/{self.token}'
