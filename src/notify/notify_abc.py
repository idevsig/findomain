from __future__ import annotations

from abc import ABC
from abc import abstractmethod

"""
Notify 推送通知
"""


class NotifyABC(ABC):
    @property
    def provider_name(self) -> str:
        """
        Returns the name of the notification provider.
        """
        return self.__class__.__name__

    @abstractmethod
    def _build_url(self, timestamp: str = "", sign: str = "") -> str:
        """
        构建请求 URL
        """
        pass

    @abstractmethod
    def send(self, message):
        """
        发送通知
        :param message: 消息内容
        """
        pass
