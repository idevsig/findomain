import random
import requests
from requests.models import Response
from lxml import etree


class HttpRequest:
    '''
    请求库
    '''

    def __init__(self, proxys=None):
        self.session = requests.Session()
        self.set_headers()
        self.update_proxys(proxys)
        self.response = Response()

    def set_headers(self):
        '''
        设置 默认header
        '''
        self.session.headers.update(self.header)

    def update_headers(self, headers):
        '''
        更新 header
        :param headers: 头信息
        '''
        self.clear_headers()
        self.session.headers.update(headers)

    def clear_headers(self):
        '''
        清空头信息 header
        '''
        self.session.headers.clear()

    def update_proxys(self, proxy=None):
        '''
        更新 proxys
        :param proxy: 代理
        '''
        if not proxy:
            return None

        self.session.proxies.update({
            'http': proxy,
            'https': proxy
        })

    def http_cookies(self, url):
        '''
        通过网址获取相应 cookies
        :param url: 网址
        '''
        response = requests.get(url)
        return str(response.cookies)

    def set_http_cookies(self, url):
        '''
        更新 cookies from url
        :param url: 网址
        '''
        self.session.headers.update(
            {'cookie': self.http_cookies(url), 'referer': url})

    def update_cookies(self, cookies):
        '''
        更新 cookies
        :param cookies: cookies
        '''
        self.session.cookies.update(cookies)

    def get(self, url, params=None, timeout=None, verify=True):
        '''
        GET 请求数据
        :param url: 网址
        :param params: 参数
        :param timeout: 超时时间
        :param verify: 校验 SSL 证书
        '''
        self.response = self.session.get(
            url, params=params, timeout=timeout, verify=verify)
        return self

    def post(self, url, data=None, files=None, timeout=None, verify=True):
        '''
        POST 请求数据
        :param url: 网址
        :param data: 数据
        :files files: 文件二进制数据
        :param timeout: 超时时间
        :param verify: 校验 SSL 证书
        '''
        self.response = self.session.post(
            url, data=data, files=files, timeout=timeout, verify=verify)
        return self

    @property
    def user_agent(self):
        """
        return an User-Agent at random
        :return:
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def default_user_agent(self):
        """
        return an default User-Agent at random
        :return:
        """
        ua_list = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.0.0 Safari/537.36 Edg/30.0.1599.101',
        ]
        return random.choice(ua_list)

    @property
    def header(self):
        """
        basic header
        :return:
        """
        return {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.default_user_agent,
            'x-requested-with': 'XMLHttpRequest',
        }

    @property
    def tree(self):
        return etree.HTML(self.response.content)

    @property
    def content(self):
        return self.response.content

    @property
    def text(self):
        return self.response.text

    @property
    def json(self):
        try:
            return self.response.json()
        except Exception as e:
            return {}
