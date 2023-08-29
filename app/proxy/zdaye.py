from lxml import etree
from .proxy import Proxy
from ..utils.request import HttpRequest
import concurrent.futures
from datetime import datetime
from time import sleep


class Zdaye(Proxy):

    def __init__(self) -> None:
        self.proxy_url = 'https://www.zdaye.com'
        self.list = []

    def generate(self):
        '''
        生成数据池
        '''
        list = []
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []

                current_date = datetime.now()
                start_url = '{}/dayProxy/{}.html'.format(
                    self.proxy_url, current_date.strftime('%Y/%-m/1'))
                req = HttpRequest()
                req.get(start_url)
                html_tree = req.tree
                latest_page_time = html_tree.xpath(
                    "//span[@class='thread_time_info']/text()")[0].strip()

                interval = current_date.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
                if interval.seconds < 7200:  # 只采集5分钟内的更新
                    target_url = "{}{}".format(self.proxy_url,
                                               html_tree.xpath(
                                                   "//h3[@class='thread_title']/a/@href")[0].strip())
                    while target_url:
                        # print(target_url)
                        req.get(target_url)
                        if req.response.status_code != 200:
                            raise ValueError(
                                f'status code {req.response.status_code}')
                        _tree = req.tree
                        for tr in _tree.xpath("//table//tr"):
                            ip = "".join(tr.xpath("./td[1]/text()")).strip()
                            port = "".join(tr.xpath("./td[2]/text()")).strip()
                            scheme = "".join(
                                tr.xpath("./td[3]/text()")).strip().lower()
                            print(ip, port, scheme)
                            url = '{}://{}:{}'.format(scheme, ip, port)

                            future = executor.submit(
                                self.validate, scheme, url)
                            futures.append(future)
                            # yield "%s:%s" % (ip, port)
                        next_page = _tree.xpath(
                            "//div[@class='page']/a[@title='下一页']/@href")
                        target_url = "{}{}".format(self.proxy_url,
                                                   next_page[0].strip()) if next_page else False
                        sleep(5)

                list = self.future(futures)

        except Exception as e:
            print(f'Error: Zdaye generate {e}')

        self.list = list
