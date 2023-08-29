import json
from ..utils.request import HttpRequest
from .proxy import Proxy
import concurrent.futures

'''
https://github.com/fate0/proxylist
http://proxylist.fatezero.org/proxy.list
'''


class Fate0(Proxy):
    def __init__(self) -> None:
        ghproxy = 'https://ghproxy.com/'
        self.proxy_url = f'{ghproxy}https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'

        self.list = []

    def generate(self):
        '''
        生成数据池
        '''
        list = []
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                req = HttpRequest()
                req.get(self.proxy_url, verify=False)

                if req.response.status_code != 200:
                    raise ValueError(f'status code {req.response.status_code}')

                json_arr = req.text.split('\n')

                for value in json_arr:
                    if not value:
                        continue

                    # JSON dict
                    item = json.loads(value)
                    scheme = item['type']
                    # 提取 proxy url
                    url = '{}://{}:{}'.format(scheme,
                                              item['host'], item['port'])

                    future = executor.submit(self.validate, scheme, url)
                    futures.append(future)
                    # break

                list = self.future(futures)

        except Exception as e:
            print(f'Error: Fate0 generate {e}')

        self.list = list
