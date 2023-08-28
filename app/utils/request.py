import requests

'''
请求库
'''


class HttpRequest:
    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.proxies = {
            'http': proxy,
            'https': proxy
        } if proxy else None

        self.headers = {}
        self.cookies = {}

        self.set_headers()

    '''
    设置 header
    '''

    def set_headers(self):
        default_headers = {
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
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.26',
            'x-requested-with': 'XMLHttpRequest',
        }
        self.update_headers(default_headers)

    '''
    更新 header
    '''

    def update_headers(self, headers):
        self.headers.update(headers)

    '''
    网页请求 cookies
    '''

    def http_cookies(self, url):
        response = requests.get(url)
        return str(response.cookies)

    '''
    更新 cookies from url
    '''

    def set_cookies(self, url):
        self.session.headers.update(
            {'cookie': self.http_cookies(url), 'referer': url})

    '''
    更新 cookies
    '''

    def update_cookies(self, cookies):
        self.cookies.update(cookies)

    '''
    更新 proxy
    '''

    def update_proxy(self, proxy):
        self.proxies = {
            'http': proxy,
            'https': proxy
        } if proxy else None

    def get(self, url, params=None):
        response = self.session.get(
            url, headers=self.headers, cookies=self.cookies, params=params, proxies=self.proxies)
        return response

    def post(self, url, data=None, files=None):
        response = self.session.post(
            url, data=data, files=files, headers=self.headers, cookies=self.cookies, proxies=self.proxies)
        return response
