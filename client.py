import random,requests
from proxy import Proxy

class Client():

    def __init__(self) -> None:
        # 设置请求句柄
        self.session = requests.Session()

        # 设置请求 headers
        self.set_headers() 

        self.ip_addresses = []
        # 设置代理 IP
        self.set_ip_proxy()            

    '''
    网页请求 cookie
    '''
    def get_http_cookie(self, url):
        response = requests.get(url)
        return str(response.cookies)    

    '''
    设置请求头
    '''
    def set_headers(self):
        self.session.headers = {
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

    '''
    设置 cookie
    '''
    def set_cookie(self, url):
        self.session.headers.update({'cookie': self.get_http_cookie(url), 'referer': url})        

    '''
    自定义代理 IP
    '''
    def set_ipaddress(self):
        return ['115.223.7.34:80', '27.192.200.7:9000', '113.237.3.178:9999', '181.10.129.85:8080']

    def set_ip_proxy(self):
        proxy = Proxy()
        # self.ip_addresses = self.set_ipaddress()  

        # self.ip_addresses = proxy.get_jiangxianli() 
        # self.ip_addresses = proxy.get_xiladaili()
        self.ip_addresses = proxy.get_fate0() 
        proxy.write_proxy(self.ip_addresses)           

    '''
    代理请求
    '''
    def proxy_request(self, url, domain, type = 'get', use_proxy = True, **kwargs):
        times = 0

        while True:
            proxy_len = len(self.ip_addresses)
            proxies = {}

            try:
                if use_proxy and proxy_len > 0:
                    proxy = random.randint(0, proxy_len - 1)
                    proxies = {"http": 'http://' + self.ip_addresses[proxy]}

                if type == 'get':
                    response = self.session.get(url, proxies=proxies, timeout=5, **kwargs)
                else:
                    response = self.session.post(url, proxies=proxies, timeout=5, **kwargs)
                   
                # print(f"Proxy currently being used: {proxy['https']}")
                # print(proxies)
                
                break
            except Exception as e:
                print('''
*********************************「ERROR START」**************************************
looking for another proxy {}
domain: {}
url: {}
try times: {}
err: {}
*********************************「ERROR END」****************************************
                '''.format(proxies, domain, url, times, e))
                # print(f'\nError: {response}\n')
                times += 1
                # 只请求 10 次
                if times == 10:
                    break
                
        return response   