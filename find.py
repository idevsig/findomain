#!/usr/bin/env python

import logging,os,json,requests
from dingtalk import Dingtalk
from domain import Domain
from whois import Whois

class Finder(object):
    def __init__(self):
        # 日志文件
        self.log_filename = 'domain.log'
        self.set_log_config()

        # 域名信息初始化
        ## 默认为 通过西部数据平台查询 3 位纯数字的 cc
        self.domain_length = 3
        self.domain_suffixes = 'cc'
        self.domain_gen_type = 1
        self.domain_characters = ''
        self.whois_isp = 'west'
        self.domain_start = ''
        self.domain_restart_url = ''

        # 启用代理
        self.proxy = False

        # 上传至
        self.transfer_url = ''

        self.set_domain_info()

        # 设置钉钉通知
        token, secret = self.set_dingtalk()
        self.notifier = Dingtalk(token=token, secret=secret)

        # 域名生成器
        self.domain_maker = Domain(self.domain_length, self.domain_characters)

        # 设置 WHOIS
        self.whois_maker = Whois(self.whois_isp, self.proxy)

    '''
    设置日志配置
    '''
    def set_log_config(self):
        # 清空文件
        open(self.log_filename,'w').truncate()   

        # 设置日志配置     
        logging.basicConfig(
                        # 控制台打印的日志级别
                        level = logging.INFO, 
                        filename = self.log_filename,

                        # 模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                        # a 是追加模式，默认如果不写的话，就是追加模式
                        filemode = 'a',
                        # 日志格式
                        format = '%(message)s'
                        )

    '''
    设置域名配置
    '''
    def set_domain_info(self):
        # print('DOMAIN_INFO: ', os.environ.get('DOMAIN_INFO'))
        info_str = os.environ.get('DOMAIN_INFO')
        if info_str == None:
            # 通过 URL 获取域名配置信息
            url_str = os.environ.get('DOMAIN_URL')
            if url_str:
                info_str = self.get_domain_info(url_str)
            
        # 解析域名配置信息
        if info_str:
            info = json.loads(info_str)
            print(info)

            try:
                self.domain_suffixes = info['suffixes']
                self.domain_length = info['length']
                self.domain_gen_type = info['type']
                self.whois_isp = info['isp']
                self.transfer_url = info['transfer']
                self.domain_characters = info['characters']
                self.domain_restart_url = info['restart_url']

                domain_start = info['start']
                if len(domain_start) == self.domain_length:                
                    self.domain_start = domain_start

                if 'proxy' in info:
                    self.proxy = info['proxy'] == 1
                else:
                    self.proxy = False

            except Exception as e:
                print(f'convert domain info err: {e}')
                exit(1)
      
    '''
    从线上获取域名配置信息
    '''
    def get_domain_info(self, url):
        try:
            response = requests.get(url)
            return response.text
        except Exception as e:
            print(f'get domain info from DOMAIN_URL {url} {e}')

        return None

    '''
    设置钉钉消息
    '''
    def set_dingtalk(self):
        DINGTALK_ROBOT_TOKEN = os.environ.get('DINGTALK_ROBOT_TOKEN')
        DINGTALK_ROBOT_SECRET = os.environ.get('DINGTALK_ROBOT_SECRET')        
        return DINGTALK_ROBOT_TOKEN,DINGTALK_ROBOT_SECRET      

    '''
    发送钉钉消息
    '''
    def push_dingtalk(self, url):
        content = open(self.log_filename,'r').read()
        print('''
----------------------Domain List------------------------
{}
---------------------------------------------------------
{}
'''.format(url, content)) 

        if url:
            content = url
        self.notifier.push(content)   

    '''
    上传查询的日志文件到 transfer
    '''
    def transfer_file(self):
        if self.transfer_url != '':
            try:
                response = requests.post(self.transfer_url, files = {'file': open(self.log_filename,'rb')}) 
                # print(f'transfer_file: {response.text}')
                return response.text
            except Exception as e:
                print(f'transfer_file err: {e}')
        return 

    '''
    生成域名列表
    '''
    def generate_domains(self):
        domains = []
        if self.domain_gen_type == 1:
            self.domain_maker.add_only_numbers()
        elif self.domain_gen_type == 2:
            self.domain_maker.add_only_characters()
        elif self.domain_gen_type == 3:
            self.domain_maker.add_only_numbers()
            domains = self.domain_maker.make_domains()
            self.domain_maker.clear_all_chars()
            self.domain_maker.add_only_characters()
        elif self.domain_gen_type == 4:
            self.domain_maker.add_only_numbers()
            self.domain_maker.add_only_characters()
        elif self.domain_gen_type == 5:
            self.domain_maker.set_custom_chars(self.domain_characters)
        else:
            self.domain_maker.add_only_numbers()

        domains_2 = self.domain_maker.make_domains()
        domains.extend(domains_2)
        # print(domains, len(domains))
        return domains

    '''
    过滤已查询过的域名
    '''
    def filter_domains(self):
        domains = []
        addit = False

        if self.domain_start == '':
            addit = True

        domain_list = self.generate_domains()
        for domain in domain_list:
            if addit:
                domains.append(''.join(domain))
            elif self.domain_start != '' and self.domain_start == domain:
                domains.append(''.join(domain))
                addit = True

        # print(domains, len(domains))
        return domains

    '''
    重置开始的域名
    '''
    def reset_start(self, character):
        if self.domain_restart_url == '':
            return

        try:
            response = requests.post(self.domain_restart_url, data = {'domain': character})
            print(f'重置开始字符为 {character}')
            # print(response.text)
            return True
        except Exception as e:
            print(f'set domain restart character {self.domain_restart_url} {e}')

        return None

    def run(self):
        # return
        domains = self.filter_domains()
        # return

        if len(domains) == 0:
            print(f'没有域名可以查询')
            return

        # 请求失败次数
        err_times = 0
        # 查询次数
        check_times = 0
        for character in domains:
            check_times += 1
            result = 0
            is_registered, regdate, expdate, err = self.whois_maker.check_registered(character, self.domain_suffixes)
            # print('registered: ', is_registered, regdate, expdate, err)

            if err == 0:
                err_times = 0
            else:
                err_times += 1

            # if check_times == 3:
            #     self.reset_start(character)
            #     break
                
            # 失败 1 次，则更新开始的域名
            if err_times == 1:
                self.reset_start(character)

            # 失败 10 次则退出程序
            if err_times == 10:
                break

            if is_registered:
                result = 1
            
            log = '{}.{},{},{},{},{}'.format(character, self.domain_suffixes, result, regdate, expdate, err)
            logging.info(log)

            # 每满 990 次，推送一次数据
            # if check_times % 990 == 0:
            #     log_url = self.transfer_file()
            #     self.push_dingtalk(log_url)   

            # break

        # 完成所有
        if err_times == 0:
            self.reset_start('-')

        # 日志文件信息
        log_url = self.transfer_file()
        self.push_dingtalk(log_url)
        

if __name__ == '__main__':
    Finder().run()
