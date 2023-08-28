from abc import ABC, abstractmethod

'''
Whois
'''


class Whois(ABC):

    '''
    是否支持该后缀
    '''
    @abstractmethod
    def supported(self, suffixes):
        pass

    '''
    生成请求 URL
    '''
    @abstractmethod
    def requrl(self):
        pass

    '''
    请求数据
    '''
    @abstractmethod
    def fetch(self):
        pass

    '''
    是否可注册
    '''
    @abstractmethod
    def available(self, domain):
        pass
