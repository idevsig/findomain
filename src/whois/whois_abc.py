from __future__ import annotations

import socket
from abc import ABC
from abc import abstractmethod
from urllib.parse import urlparse

from requests import Response
from type.domain import QueryResult


class WhoisABC(ABC):
    """
    WhoisABC
    """

    _supported_suffixes = []

    def __init__(self):
        # 在类的实例化时，将 _enable 默认设置为 True
        self._enable: bool = True

    @property
    def provider_name(self) -> str:
        """
        Returns the name of the WHOIS provider.
        """
        return self.__class__.__name__

    @property
    def enable(self) -> bool:
        """
        Returns the enable status of the WHOIS provider.
        """
        return self._enable

    @enable.setter  # 添加 setter 方法
    def enable(self, value: bool):
        """
        Sets the enable status of the WHOIS provider.
        :param value: The new enable status.
        """
        if not isinstance(value, bool):
            raise TypeError("enable must be a boolean")
        self._enable = value

    @property
    def base_url(self) -> str:
        """
        Returns the base URL for the WHOIS provider's API.
        """
        return self._base_url  # 从内部变量获取值

    @base_url.setter  # 添加 setter 方法
    def base_url(self, value: str):
        """
        Sets the base URL for the WHOIS provider's API.
        :param value: The new base URL.
        """
        # 你可以在这里添加验证逻辑，例如检查是否是合法的URL
        if not isinstance(value, str):
            raise TypeError("base_url must be a string")
        self._base_url = value  # 将新值赋给内部变量

    @property
    def supported_suffixes(self) -> str:
        """
        Returns the supported suffixes for the WHOIS provider's API.
        """
        return self._supported_suffixes  # 从内部变量获取值

    @supported_suffixes.setter  # 添加 setter 方法
    def supported_suffixes(self, value: list[str]):
        """
        Sets the base URL for the WHOIS provider's API.
        :param value: The new base URL.
        """
        # 第一步：检查 value 是否是一个列表 (list)
        if not isinstance(value, list):
            raise TypeError("supported_suffixes must be a list.")

        # 第二步：检查列表中的所有元素是否都是字符串 (str)
        # 使用 all() 和列表推导式或生成器表达式进行高效检查
        if not all(isinstance(item, str) and len(item) > 1 for item in value):
            raise TypeError(
                "All items in supported_suffixes list must be strings.",
            )

        self._supported_suffixes = value

    @property
    def base_host(self) -> str:
        """
        Returns the base host for the WHOIS provider's API.
        """
        base_url = urlparse(self.base_url)
        return base_url.hostname if base_url.hostname else ""

    def _is_service_available(self) -> bool:
        """检查服务是否可用"""
        try:
            if not self.base_host:
                raise ValueError(
                    "Error: base_host is empty, cannot check service availability.",
                )

            socket.gethostbyname(self.base_host)
            return True
        except socket.gaierror as e:
            # Use 'e' only within this block
            raise ValueError(
                f"DNS resolution failed for {self.base_host}: {e}",
            )
        except Exception as e:
            # Use 'e' only within this block
            raise ValueError(
                f"An unexpected error occurred during service availability check: {e}",
            )

    def supported(self, suffix):
        """
        是否支持该后缀
        :param suffix: 后缀
        """
        try:
            (self.supported_suffixes.index(suffix) if self.supported_suffixes else True)
        except Exception:
            raise ValueError(
                f"Error: ({self.provider_name}) this suffix is not supported: {suffix}",
            )

    @abstractmethod
    def _make_request_url(self) -> str:
        """
        生成请求 URL
        """

    @abstractmethod
    def fetch(self, url: str, domain: str) -> Response:
        """
        请求数据
        """

    @abstractmethod
    def query(self, domain) -> QueryResult:
        """
        查询域名
        :param domain: 域名
        """
