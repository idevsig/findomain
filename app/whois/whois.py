from abc import ABC, abstractmethod


class Whois(ABC):
    '''
    Whois
    '''
    @abstractmethod
    def supported(self, suffixes):
        '''
        是否支持该后缀
        '''
        pass

    @abstractmethod
    def requrl(self):
        '''
        生成请求 URL
        '''
        pass

    @abstractmethod
    def fetch(self):
        '''
        请求数据
        '''
        pass

    @abstractmethod
    def available(self, domain):
        '''
        是否可注册
        '''
        pass
