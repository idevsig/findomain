from __future__ import annotations

import random
import time
from http.cookiejar import CookieJar
from typing import Any

import requests
from lxml import etree
from requests import Response
from requests import Session
from requests.exceptions import ConnectionError
from requests.exceptions import JSONDecodeError
from requests.exceptions import RequestException
from requests.exceptions import SSLError
from requests.exceptions import Timeout
from urllib3.exceptions import NameResolutionError


class HttpRequest:
    """封装 requests 库的 HTTP 客户端，支持代理、请求头、Cookie 管理及重试机制。"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ]

    SUPPORTED_METHODS = {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "HEAD",
        "OPTIONS",
        "PATCH",
    }

    def __init__(self, proxies: dict[str, str] | None = None):
        self.auth: tuple[str, str] | None = None  # username, password
        self.session: Session = requests.Session()
        self.update_headers()
        self.update_proxies(proxies)
        self._response: Response | None = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "DNT": "1",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": random.choice(self.USER_AGENTS),
            "X-Requested-With": "XMLHttpRequest",
        }

    def set_auth(self, username: str, password: str):
        self.auth = (username, password)
        return self

    def update_headers(self, headers: dict[str, str] | None = None):
        self.session.headers.clear()
        self.session.headers.update(headers or self._default_headers())
        return self

    def update_proxies(self, proxies: dict[str, str] | None = None):
        if proxies:
            self.session.proxies.update(proxies)
        return self

    def update_cookies(self, cookies: dict[str, str] | CookieJar):
        self.session.cookies.update(cookies)
        return self

    def fetch_cookies_from_url(
        self,
        url: str,
        timeout: float = 10,
    ) -> CookieJar:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.cookies
        except RequestException as e:
            raise RequestException(
                f"Failed to fetch cookies from {url}: {e}",
            ) from e

    def set_cookies_from_url(self, url: str, timeout: float = 10):
        cookies = self.fetch_cookies_from_url(url, timeout)
        self.update_cookies(cookies)
        self.session.headers["Referer"] = url

    def _request_method_handler(
        self,
        method: str,
        url: str,
        retries: int = 3,
        backoff: float = 1.0,
        auth: tuple[str, str] | None = None,
        **kwargs,
    ) -> Response:
        if method.upper() not in self.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if auth is None and self.auth is not None:
            kwargs["auth"] = self.auth
        elif auth:
            kwargs["auth"] = auth

        for attempt in range(retries + 1):
            try:
                response = getattr(self.session, method.lower())(url, **kwargs)
                response.raise_for_status()
                return response
            except (
                NameResolutionError,
                ConnectionError,
                Timeout,
                SSLError,
            ) as e:
                if attempt >= retries:
                    raise RequestException(
                        f"Request failed after {retries + 1} attempts: {e}",
                    ) from e
                time.sleep(backoff * (2**attempt))
                if isinstance(e, Timeout):
                    kwargs["timeout"] = kwargs.get("timeout", 10) * 1.5
                if isinstance(e, SSLError):
                    kwargs["verify"] = False
            except RequestException as e:
                raise RequestException(
                    f"{method.upper()} request failed for {url}: {e}",
                ) from e

        raise RequestException("Unreachable error in retry logic")

    def _request(
        self,
        method: str,
        url: str,
        retries: int = 2,
        auth: tuple[str, str] | None = None,
        **kwargs,
    ) -> HttpRequest:
        self._response = self._request_method_handler(
            method,
            url,
            retries=retries,
            auth=auth,
            **kwargs,
        )
        return self

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        timeout: float = 10,
        verify: bool = True,
        retries: int = 2,
        auth: tuple[str, str] | None = None,
    ) -> HttpRequest:
        return self._request(
            "GET",
            url,
            params=params,
            timeout=timeout,
            verify=verify,
            retries=retries,
            auth=auth,
        )

    def post(
        self,
        url: str,
        data: dict[str, Any] | bytes | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: float = 10,
        verify: bool = True,
        retries: int = 2,
        auth: tuple[str, str] | None = None,
    ) -> HttpRequest:
        return self._request(
            "POST",
            url,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify=verify,
            retries=retries,
            auth=auth,
        )

    def put(
        self,
        url: str,
        data: dict[str, Any] | bytes | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        timeout: float = 10,
        verify: bool = True,
        retries: int = 2,
        auth: tuple[str, str] | None = None,
    ) -> HttpRequest:
        return self._request(
            "PUT",
            url,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
            verify=verify,
            retries=retries,
            auth=auth,
        )

    @property
    def response(self) -> Response:
        if self._response is None:
            raise ValueError("No request has been made yet.")
        return self._response

    @property
    def content(self) -> bytes:
        return self.response.content

    @property
    def text(self) -> str:
        return self.response.text

    @property
    def json(self) -> dict[str, Any]:
        try:
            return self.response.json()
        except (ValueError, JSONDecodeError):
            return {}

    @property
    def tree(self) -> etree._Element:
        return etree.HTML(self.response.content)
