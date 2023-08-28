from abc import ABC, abstractmethod

'''
Notify 推送通知
'''


class Notify(ABC):

    '''
    签名
    '''
    @abstractmethod
    def signature(self):
        pass

    '''
    发送通知
    '''
    @abstractmethod
    def send(self, message):
        pass
