from lxml import etree
from .proxy import Proxy
from ..utils.request import HttpRequest
import concurrent.futures
from datetime import datetime
from time import sleep


class Ip66(Proxy):

    def __init__(self) -> None:
        self.proxy_url = 'http://www.66ip.cn'
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
                req.get(self.proxy_url, timeout=10)

                if req.response.status_code != 200:
                    raise ValueError(f'status code {req.response.status_code}')

                reqtree = req.tree
                for i, tr in enumerate(reqtree.xpath("(//table)[3]//tr")):
                    if i > 0:
                        ip = "".join(tr.xpath("./td[1]/text()")).strip()
                        port = "".join(tr.xpath("./td[2]/text()")).strip()

                        future = executor.submit(
                            self.validate, 'http', 'http://{}:{}'.format(ip, port))
                        futures.append(future)

                list = self.future(futures)

        except Exception as e:
            print(f'Error: Ip66 generate {e}')

        self.list = list
