from __future__ import annotations

import logging
import os
import random
from datetime import datetime

import json5
from notifier import send_notify
from type.domain import QueryResult
from type.enum import Query
from utils.domain import Domain
from utils.request import HttpRequest
from utils.util import is_valid_url
from utils.util import replace_url_at
from whois.qcloud import Qcloud
from whois.rapidapi import Rapidapi
from whois.west import West
from whois.whois_abc import WhoisABC
from whois.zzidc import Zzidc


class App:
    def __init__(self, config) -> None:
        self.config = config

        # 需查询的域名列表
        self.domains: list[str] = []
        # 最后一次查询失败的域名
        self.last_failed_domain = ''
        # 域名提供商列表
        self.dnp_list: list[WhoisABC] = []
        # 域名提供商数量
        self.dnp_count = 0
        # 查询结果
        self.results: list[QueryResult] = []
        # 结果保存位置文件名
        file_name = f'{datetime.now().strftime("%Y%m%d")}_{self.config.setting.result_file}'
        self.result_file = os.path.join(self.config.setting.log_dir, file_name)

    def prepare(self, custom_domain=None):
        # 从环境变量中获取自定义域名
        if custom_domain:
            self.domains = [custom_domain]
            self.config.domain.done = Query.NotDone.value
        elif self.config.setting.url:
            self.domain_from_url(self.config.setting.url)
        else:
            self.generator()

        self.__load_DNP()
        return self

    def domain_from_url(self, url):
        """
        从线上获取域名配置信息
        """
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
            self.config.domain.update_from_dict(json5.loads(req.text))
        except Exception as e:
            raise ValueError(
                f'Get domain info from url {url} failed: {e}.',
            ) from e

    def __load_DNP(self):
        """
        加载域名提供商
        """
        dnp_list = [
            West(),
            Qcloud(),
            Zzidc(),
            Rapidapi(),
        ]
        self.dnp_list = [service for service in dnp_list if service.enable]

        # 自定义域名提供商
        if self.config.whois.dnp:
            arr = str(self.config.whois.dnp).replace(' ', '').split(',')
            self.filter_dnps(arr)
        # 域名提供商的数量
        self.dnp_count = len(self.dnp_list)

    def filter_dnps(self, dnp_arr):
        """
        筛选域名提供商
        """
        dnps = []
        for name in dnp_arr:
            # dnps 遍历
            for dnp in self.dnp_list:
                # dnp 名转小写
                dnp_name = str(dnp.provider_name).lower()
                # 匹配名称
                if name == dnp_name:
                    if dnp.supported(self.config.domain.suffixes):
                        dnps.append(dnp)
                    # 数据已匹配，跳出此循环
                    break
        self.dnp_list = dnps
        return self

    def _check_dnps(self):
        """
        检查域名提供商列表
        """
        if len(self.dnp_list) == 0:
            raise ValueError('No whois provider available.')
        return self

    def generator(self):
        """
        UP: 生成域名列表
        :param domain: 域名信息
        """
        # 域名已全部查询完成
        if self.config.domain.done == Query.Done.value:
            raise ValueError('Domain query complete.')

        self.domains = Domain(self.config.domain).maker()

        if len(self.domains) == 0:
            raise ValueError('No domain available for querying.')

    #     def domain_resume(self, domain):
    #         '''
    #         断点查询，更新域名信息到服务器
    #         :param domain: 域名，含后缀
    #         '''
    #         if not self.setting['url']:
    #             return
    #         try:
    #             start_char = ''
    #             done = 0 if domain else 1
    #             if done == 0:
    #                 # 取域名，去除后缀，更新至断点续查服务器
    #                 parts = domain.split(".")
    #                 start_char = parts[0]

    #             data = {
    #                 'suffixes': self.domain['suffixes'],
    #                 'length': self.domain['length'],
    #                 'mode': self.domain['mode'],
    #                 'alphabets': self.domain['alphabets'],
    #                 'start_char': start_char,
    #                 'prefix': self.domain['prefix'],
    #                 'suffix': self.domain['suffix'],
    #                 'done': done,
    #             }
    #             data = json.dumps(data, indent=4)
    #             req = HttpRequest()
    #             req.post(self.setting['url'], data.encode('utf-8'))
    #             print(f"Update domain info: {req.text}")
    #         except Exception as e:
    #             print(f"Update domain info failed.")

    def fetch(self):
        """
        抓取 whois 数据
        """
        if self.dnp_count == 0:
            raise ValueError('No whois provider available.')

        count = 0  # 成功查询次数
        max_retries = 3  # 最多重试3次

        # 从配置中获取最大重试次数
        if (
            isinstance(self.config.setting.max_retries, int)
            and self.config.setting.max_retries >= 3
        ):
            max_retries = self.config.setting.max_retries

        # 遍历域名
        for domain in self.domains:
            # print(domain)
            retries = 0  # 重试次数计数器
            should_break = False  # 标志，用于控制是否跳出最外层的for循环

            # 重试查询
            while retries < max_retries:
                try:
                    # 随机选择一个 whois 提供商
                    dnp = random.choice(self.dnp_list)

                    # 调用 whois 查询
                    result = dnp.query(domain)

                    # whois 查询失败，打印日志并抛出异常
                    if not result.is_success:  # 错误码不为0
                        # 打印日志
                        logging.error(result)  # 错误日志
                        raise ValueError(
                            f'fetch {domain} failed from {dnp.provider_name}, retries: {retries}',
                        )

                    logging.info(result)  # 成功日志
                    # 增加成功数
                    count += 1

                    # 保存结果
                    self.results.append(result)

                    break
                except Exception as e:
                    # 增加重试次数
                    retries += 1
                    logging.warning(
                        f'Fetch err: {e}, retries: {retries}, dnp: {dnp.provider_name}',
                    )
                    if retries >= max_retries:
                        logging.error(
                            f'Max retries reached fetch domain {domain} info, exiting loop.',
                        )
                        # 设置标志以跳出最外层的for循环
                        should_break = True
                        break  # 达到最大重试次数，退出循环
                    continue

            # 如果标志被设置，跳出最外层的for循环
            if should_break:
                self.last_failed_domain = domain
                break

        if count == 0:
            raise ValueError('Failed to retrieve valid domain data.')

    def save_domain_list(self):
        """
        保存域名列表
        """
        save_path = os.path.join(
            self.config.setting.log_dir,
            self.config.setting.domain_file,
        )
        with open(save_path, 'w') as f:
            f.write('\n'.join(self.domains))
        return self

    def save_result_csv(self):
        """
        保存查询结果
        """
        with open(self.result_file, 'w') as f:
            f.write(
                'domain, available, registration_date, expiration_date, error_code, provider\n',
            )
            for result in self.results:
                f.write(f'{result.to_string()}\n')
        return self

    def upload_result_csv(self):
        """
        上传查询结果
        """
        # 检查 server_url 是否配置
        if not self.config.setting.server_url:
            return []

        # 检测 URL 是否合法
        if not is_valid_url(self.config.setting.server_url):
            raise ValueError(
                f'Invalid server url: {self.config.setting.server_url}',
            )

        # 检查 server_url 是否以 http 或 https 开头
        if not self.config.setting.server_url.startswith(
            'http',
        ) and not self.config.setting.server_url.startswith('https'):
            raise ValueError('Transfer url must start with http or https.')

        # 检查文件是否存在
        if not os.path.exists(self.result_file):
            raise ValueError(f'File {self.result_file} not found.')

        upload_info = []
        server_url = replace_url_at(self.config.setting.server_url)

        # user:password 转为元组 (user, password)
        auth = (
            tuple(
                self.config.setting.server_auth.split(
                    ':',
                ),
            )
            if self.config.setting.server_auth
            else None
        )

        # 打开文件并上传
        try:
            with open(self.result_file, 'rb') as file:
                req = HttpRequest()
                req.put(server_url, data=file, auth=auth)
                if (
                    req.response.status_code != 200
                    and req.response.status_code != 201
                ):
                    raise ValueError(
                        f'Upload result file failed, status code {req.response.status_code}',
                    )

                upload_info.append(req.text if req.text else server_url)
                x_url_delete = req.response.headers.get('x-url-delete')

                if x_url_delete:
                    upload_info.append(x_url_delete)

        except Exception as e:
            raise ValueError(f'Upload result file failed: {e}') from e

        return upload_info

    def run(self, custom_domain=None):
        # 简单判断域名是否合法
        if custom_domain and '.' not in custom_domain:
            logging.error(f'Invalid domain: {custom_domain}')
            return

        logging.debug(self.config.json())

        try:
            self.prepare(custom_domain).fetch()
            self.save_domain_list()

            # 保存查询的数据
            self.save_result_csv()

            # 上传到服务器
            upload_info = self.upload_result_csv()
            if upload_info:
                upload_url, *rest = upload_info
                logging.info(f'Upload result file to {upload_url}')
                if rest:
                    logging.info(f'Delete url: {rest[0]}')

            # 发送通知
            send_notify(self.config.notify, upload_info, self.result_file)
        except Exception as e:
            print(f'Error: {e}')
