from abc import ABC, abstractmethod

'''
Notify 推送通知
'''


class Notify(ABC):

    @abstractmethod
    def signature(self):
        '''
        签名
        '''
        pass

    @abstractmethod
    def send(self, message):
        '''
        发送通知
        :param message: 消息内容
        '''
        pass
