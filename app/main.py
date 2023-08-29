import logging
from datetime import datetime
import random
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

        # 初始化 ISP
        self.init_isp()

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
    初始化 ISP
    '''

    def init_isp(self):
        # 全部
        self.isps = [
            West(),
            Qcloud(),
            Zzidc(),
            Rapidapi()
        ]

        # 自定义 ISP 商
        if self.whois['isp']:
            arr = str(self.whois['isp']).split(',')
            isps = []

            # 配置中的 ISPS 遍历
            for name in arr:
                # ISPS 遍历
                for isp in self.isps:
                    # ISP 名转小写
                    isp_name = str(isp.__class__.__name__).lower()
                    # 匹配名称
                    if name == isp_name:
                        supported = isp.supported(self.domain['suffixes'])
                        # ISP 不支持此后缀
                        if not supported:
                            print(
                                f'{isp_name} suffixes supported: {supported}')
                        else:  # 支持的 ISP
                            isps.append(isp)
                        # 数据已匹配，跳出此循环
                        break
            # 若存在自定义 ISP，则更新
            if len(isps) > 0:
                self.isps = isps

        # 获取 ISP 数量
        self.isp_count = len(self.isps)

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

    '''
    随机 ISP
    '''

    def random_isp(self):
        idx = random.randint(0, len(self.isps) - 1)
        return self.isps[idx]

    def fetch(self):
        count = 0

        for domain in self.domains:
            # print(domain)
            retries = 0  # 重试次数计数器
            max_retries = 10  # 最多重试10次
            should_break = False  # 标志，用于控制是否跳出最外层的for循环

            while retries < max_retries:
                try:
                    isp = self.random_isp()
                    isp_name = isp.__class__.__name__
                    available, regdate, expdate, err = isp.available(domain)

                    # 打印日志
                    print(f'{domain}, {available}, {regdate}, {expdate}, {err}')

                    # whois 查询失败
                    if err != 0:
                        raise ValueError(
                            f'{isp_name} fetch domain {domain} failed.')

                    logging.info(
                        f'{domain}, {1 if available else 0 }, {err}, {regdate}, {expdate}')
                    count += 1  # 增加成功数
                    break
                except Exception as e:
                    print(f'transfer_file err: {e}')
                    retries += 1  # 增加重试次数
                    if retries >= max_retries:
                        print("Max retries reached. Exiting loop.")
                        should_break = True  # 设置标志以跳出最外层的for循环
                        break  # 达到最大重试次数，退出循环
                    continue

            if should_break:
                break  # 如果标志被设置，跳出最外层的for循环
        if count == 0:
            die('Failed to retrieve valid domain data.')

    def run(self):
        print("Domain:", self.domain)
        print("Notify:", self.notify)
        print("\n")

        # print(self.domains)
        self.fetch()

        log_path = self.setting['log_path']
        transfer_url = self.transfer_file(log_path)
        message = self.read_log(log_path, transfer_url)
        self.push(message)
