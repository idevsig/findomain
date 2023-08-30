import json
import logging
import os
import random
from datetime import datetime
from config.config_loader import load_config
from .proxy.fate0 import Fate0
from .proxy.zdaye import Zdaye
from .proxy.ip66 import Ip66
from .utils.request import HttpRequest
from .notify.feishu import Feishu
from .notify.dingtalk import Dingtalk
from .utils.helpers import die, write_file
from .utils.domain import Domain
from .whois.west import West
from .whois.qcloud import Qcloud
from .whois.rapidapi import Rapidapi
from .whois.zzidc import Zzidc


class App:
    def __init__(self, cfg_path='config.yml') -> None:

        config = self.config(cfg_path)

        # 需查询的域名列表
        self.domains = []
        # 查询失败的域名
        self.failed_domain = ''

        # 当前日期
        current_date = datetime.now().strftime("%Y%m%d")

        # 默认 setting
        default_setting = {
            'url': '',
            'transfer': '',

            'data_path': 'domain.txt',
            'log_path': 'domain.log',
            'max_retries': 3,
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
            'done': 0,
        }
        self.domain = {**default_domain, **config.get('domain', {})}
        self.domain_from_url(self.setting['url'])
        self.generator(self.domain)

        default_notify_secret = {'token': '', 'secret': ''}
        default_notify = {
            'enable': '',
            'dingtalk': default_notify_secret,
            'feishu': default_notify_secret,
        }
        self.notify = {**default_notify, **config.get('notify', {})}

        # 初始化 ISP
        self.init_isp()

        # 初始化 Proxy（未启用，停止开发）
        # self.init_proxy()

        # print("Setting:", self.setting)
        # print("Whois:", self.whois)
        # print("Domain:", self.domain)
        # print("Notify:", self.notify)
        # print("\n")

    def config(self, file_path):
        '''
        从服务器获取 config.yml 配置信息
        :param file_path: 配置文件地址
        '''
        url = os.environ.get('YAML_URL')
        if url:
            try:
                req = HttpRequest()
                req.get(url)
                if req.response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(req.content)
                else:
                    raise ValueError(f'status code {req.response.status_code}')
            except Exception as e:
                print(f'Get yaml from url {url}, {e}')

        return load_config(file_path)

    def setlog(self, logpath):
        '''
        设置日志配置
        :param logpath: 日志文件地址
        '''
        if not logpath:
            return

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

    def domain_from_url(self, url):
        '''
        从线上获取域名配置信息
        {
            "suffixes": "cn",
            "length": 3,
            "mode": 2,
            "alphabets": "",
            "start_char": "",
            "prefix": "",
            "suffix": "",
            "done": 0,
        }
        :param url: 域名信息网址
        '''
        if not url:
            return None
        try:
            req = HttpRequest()
            req.update_headers({})
            req.get(url)

            # 获取失败
            if req.response.status_code != 200:
                raise ValueError(f'status code {req.response.status_code}')

            # 更新域名信息
            self.domain.update(json.loads(req.text))
        except Exception as e:
            die(f'Get domain info from url {url} failed: {e}.')

    def init_isp(self):
        '''
        初始化 ISP
        '''
        # 全部
        self.isp_list = [
            West(),
            Qcloud(),
            Zzidc(),
            # Rapidapi()
        ]

        # 自定义 ISP 商
        if self.whois['isp']:
            arr = str(self.whois['isp']).split(',')
            isps = []

            # 配置中的 ISPS 遍历
            for name in arr:
                # ISPS 遍历
                for isp in self.isp_list:
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
                self.isp_list = isps

        # 获取 ISP 数量
        self.isp_count = len(self.isp_list)

    def init_proxy(self):
        '''
        初始化 Proxy
        '''
        print(self.whois)
        if self.whois['proxy']:
            proxys = [
                # Fate0(),
                # Zdaye(), // 有防火墙
                # Ip66(),
            ]
            list = []
            # 遍历代理服务获取数据
            for p in proxys:
                print(p.__class__.__name__)
                # 生成列表
                p.generate()
                print(p.list, len(p.list))
                list.append(p.list)

    def generator(self, domain):
        '''
        生成域名列表
        :param domain: 域名信息
        '''
        # 域名已全部查询完成
        if self.domain['done'] == 1:
            die('Domain query complete.')

        domains = Domain(domain).maker()

        if len(domains) == 0:
            die('No domain available for querying.')

        domain_strings = "\n".join(domains)
        write_file(self.setting['data_path'], domain_strings)
        self.domains = domains

    def push(self, message):
        '''
        推送通知
        :param message: 消息内容
        '''
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

    def transfer_file(self, log_path):
        '''
        上传日志文件到 transfer
        :param log_path: 日志文件路径
        '''
        if not self.setting['transfer']:
            return False
        try:
            req = HttpRequest()
            req.post(
                self.setting['transfer'], files={'file': open(log_path, 'rb')})

            if req.response.status_code != 200:
                raise ValueError(
                    f'{req.text}, status code {req.response.status_code}')

            # print(f'transfer_file: {response.text}')
            return req.text
        except Exception as e:
            print(f'transfer_file err: {e}')
            return None

    def domain_log(self, log_path, url=''):
        '''
        读取域名结果
        :param log_path: 域名结果文件路径
        :param url: transfer 文件保存路径
        '''
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

    def domain_resume(self, domain):
        '''
        断点查询，更新域名信息到服务器
        :param domain: 域名，含后缀
        '''
        if not self.setting['url']:
            return
        try:
            start_char = ''
            done = 0 if domain else 1
            if done == 0:
                # 取域名，去除后缀，更新至断点续查服务器
                parts = domain.split(".")
                start_char = parts[0]

            data = {
                'suffixes': self.domain['suffixes'],
                'length': self.domain['length'],
                'mode': self.domain['mode'],
                'alphabets': self.domain['alphabets'],
                'start_char': start_char,
                'prefix': self.domain['prefix'],
                'suffix': self.domain['suffix'],
                'done': done,
            }
            data = json.dumps(data, indent=4)
            req = HttpRequest()
            req.post(self.setting['url'], data.encode('utf-8'))
            print(f'Update domain info: {req.text}')
        except Exception as e:
            print(f'Update domain info failed.')

    def fetch(self):
        '''
        抓取 whois 数据
        '''
        count = 0  # 成功查询次数
        max_retries = 3  # 最多重试3次
        if 'max_retries' in self.setting and isinstance(self.setting['max_retries'], int) and self.setting['max_retries'] >= 3:
            max_retries = self.setting['max_retries']

        for domain in self.domains:
            # print(domain)
            retries = 0  # 重试次数计数器
            should_break = False  # 标志，用于控制是否跳出最外层的for循环

            while retries < max_retries:
                try:
                    isp = random.choice(self.isp_list)
                    isp_name = isp.__class__.__name__
                    available, regdate, expdate, err = isp.available(domain)

                    # 打印日志
                    dlog = f'{domain}, {1 if available else 0 }, {err}, {regdate}, {expdate}'
                    print(dlog)

                    # whois 查询失败
                    if err != 0:
                        raise ValueError(
                            f'{isp_name} fetch domain {domain} failed.')

                    # 写入域名结果文件
                    logging.info(dlog)
                    # 增加成功数
                    count += 1
                    # should_break = True  # denug
                    break
                except Exception as e:
                    # 增加重试次数
                    retries += 1
                    print(
                        f'Fetch domain info err: {e}, retries: {retries}')
                    if retries >= max_retries:
                        print(
                            f'Max retries reached fetch domain {domain} info, exiting loop.')
                        # 设置标志以跳出最外层的for循环
                        should_break = True
                        break  # 达到最大重试次数，退出循环
                    continue

            # 如果标志被设置，跳出最外层的for循环
            if should_break:
                self.failed_domain = domain
                break

        if count == 0:
            die('Failed to retrieve valid domain data.')

    def run(self):
        # die(len(self.domains))
        self.fetch()

        log_path = self.setting['log_path']
        transfer_url = self.transfer_file(log_path)
        message = self.domain_log(log_path, transfer_url)
        self.push(message)
        self.domain_resume(self.failed_domain)
