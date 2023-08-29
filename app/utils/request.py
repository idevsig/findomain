import random
import requests
from requests.models import Response
from lxml import etree

'''
请求库
'''


class HttpRequest:
    def __init__(self, proxys=None):
        self.session = requests.Session()
        self.set_headers()
        self.update_proxys(proxys)
        self.response = Response()

    '''
    设置 header
    '''

    def set_headers(self):
        self.session.headers.update(self.header)

    '''
    更新 header
    '''

    def update_headers(self, headers):
        self.session.headers.update(headers)

    '''
    更新 proxys
    '''

    def update_proxys(self, proxy=None):
        if not proxy:
            return None

        self.session.proxies.update({
            'http': proxy,
            'https': proxy
        })

    '''
    网页请求 cookies
    '''

    def http_cookies(self, url):
        response = requests.get(url)
        return str(response.cookies)

    '''
    更新 cookies from url
    '''

    def set_http_cookies(self, url):
        self.session.headers.update(
            {'cookie': self.http_cookies(url), 'referer': url})

    '''
    更新 cookies
    '''

    def update_cookies(self, cookies):
        self.session.cookies.update(cookies)

    def get(self, url, params=None, timeout=None, verify=True):
        self.response = self.session.get(
            url, params=params, timeout=timeout, verify=verify)
        return self

    def post(self, url, data=None, files=None, timeout=None, verify=True):
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
    def header(self):
        """
        basic header
        :return:
        """
        return {'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.8'}

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
