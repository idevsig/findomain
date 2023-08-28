import logging
from datetime import datetime
from config.config_loader import load_config
from .utils.request import HttpRequest
from .notify.feishu import Feishu
from .notify.dingtalk import Dingtalk
from .utils.helpers import die
from .utils.domain import Domain
from .whois.west import West
from .whois.qcloud import Qcloud
from .whois.rapidapi import Rapidapi
from .whois.zzidc import Zzidc


class App:
    def __init__(self, config='config.yml') -> None:

        config = load_config(config)

        # 需查询的域名列表
        self.domains = []

        # 当前日期
        current_date = datetime.now().strftime("%Y%m%d")

        # 默认 setting
        default_setting = {
            'url': '',
            'transfer': '',

            'data_path': 'domain.txt',
            'log_path': 'domain.log',
        }
        self.setting = {**default_setting, **config.get('setting', {})}
        self.setting['log_path'] = f'{current_date}_{self.setting["log_path"]}'
        self.setlog(self.setting['log_path'])

        # 默认 whois
        default_whois = {
            'isp': 'west',
            'proxy': False,
        }
        self.whois = {**default_whois, **config.get('whois', {})}

        # 默认 domain
        default_domain = {
            'suffixes': 'cn',
            'length': 3,
            'mode': 1,
            'alphabets': '',
            'start_char': '',
            'prefix': '',
            'suffix': '',
        }
        self.domain = {**default_domain, **config.get('domain', {})}
        self.generator(self.domain)

        default_notify_secret = {'token': '1', 'secret': '2'}
        default_notify = {
            'enable': '',
            'dingtalk': default_notify_secret,
            'feishu': default_notify_secret,
        }
        self.notify = {**default_notify, **config.get('notify', {})}

        setting = config['setting']
        whois = config['whois']

        print("Setting:", setting)
        print("Whois:", whois)

    '''
    设置日志配置
    '''

    def setlog(self, logpath):
        # 清空文件
        open(logpath, 'w').truncate()

        # 设置日志配置
        logging.basicConfig(
            # 控制台打印的日志级别
            level=logging.INFO,
            filename=logpath,

            # 模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
            # a 是追加模式，默认如果不写的话，就是追加模式
            filemode='a',
            # 日志格式
            format='%(message)s'
        )

    '''
    生成域名列表
    '''

    def generator(self, domain):
        domains = Domain(domain).maker()

        if len(domains) == 0:
            die('No domain available for querying.')

        domain_strings = "\n".join(domains)
        self.write_file(self.setting['data_path'], domain_strings)

        self.domains = domains
        pass

    '''
    数据写入文件
    '''

    def write_file(self, file_path, str):
        with open(file_path, "w") as file:
            file.write(str)

    '''
    推送通知
    '''

    def push(self, message):
        if not self.notify['enable']:
            return

        print(self.notify['enable'])
        providers = str(self.notify['enable']).replace(' ', '').split(',')

        try:
            # 遍历推送通知
            for provider in providers:
                notify = None
                if provider == 'dingtalk':
                    notify = Dingtalk(
                        self.notify[provider]['token'], self.notify[provider]['secret'])
                elif provider == 'feishu':
                    notify = Feishu(
                        self.notify[provider]['token'], self.notify[provider]['secret'])

                if notify:
                    # 发送消息
                    notify.send(message)

        except Exception as e:
            print(f'Sending message failed: {e}')

    '''
    读取日志
    '''

    def read_log(self, log_path, url=''):
        content = open(log_path, 'r').read()
        print('''
----------------------Domain List------------------------
{}
---------------------------------------------------------
'''.format(content))

        # 若存在 URL，则推送内容为 URL
        if url:
            content = url
        return content

    '''
    上传日志文件到 transfer
    '''

    def transfer_file(self, log_path):
        print(self.setting['transfer'])
        if self.setting['transfer']:
            try:
                req = HttpRequest()
                response = req.post(
                    self.setting['transfer'], files={'file': open(log_path, 'rb')})

                if response.status_code != 200:
                    raise ValueError(
                        f'{response.text}, status code {response.status_code}')

                # print(f'transfer_file: {response.text}')
                return response.text
            except Exception as e:
                print(f'transfer_file err: {e}')
                return None

    def run(self):
        print("Domain:", self.domain)
        print("Notify:", self.notify)
        print("\n")

        # print(self.domains)

        isp = Zzidc()
        supported = isp.supported(self.domain['suffixes'])
        print(f'supported: {supported}')
        for domain in self.domains:
            print(domain)
            res = isp.available(domain)
            print(res)
            break

        logging.info(datetime.now())
        log_path = self.setting['log_path']
        transfer_url = self.transfer_file(log_path)
        message = self.read_log(log_path, transfer_url)
        self.push(message)
