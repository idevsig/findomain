from abc import ABC, abstractmethod
import concurrent.futures

from ..utils.request import HttpRequest

'''
Proxy
'''


class Proxy(ABC):

    @abstractmethod
    def generate(self):
        '''
        生成数据池
        '''
        pass

    def validate(self, scheme, url):
        '''
        验证代理地址是否可用
        '''
        # 检测代理是否有效
        check_url = 'https://www.baidu.com'
        check_url = 'https://www.devdo.cn'
        print(f'validate: {url}')
        try:
            proxy = ''
            if scheme == 'http' or scheme == 'https':
                proxy = url
            else:
                raise ValueError(
                    f'Unsupported protocol {scheme}')

            req = HttpRequest(proxy)
            req.update_headers({
                'X-Forwarded-For': url,
            })
            req.get(check_url, timeout=5)
            if req.response.status_code != 200:
                raise ValueError(f'status code {req.response.status_code}')

            return url
        except Exception as e:
            # print(f'Proxy address unavailable, {e}')
            print(f'Proxy address unavailable {url}')
            return None

    def future(self, futures):
        '''
        迭代
        '''
        list = []
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    list.append(data)
            except Exception as e:
                print(f'Error: get proxy {e}')
        return list
