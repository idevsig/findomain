import json
from pickle import FALSE
import random
from enum import Enum

import requests

from client import Client

class ISP(Enum):
    WEST = 'west'

class Whois(object):

    def __init__(self, isp = 'west', proxy = False):
        self.session = Client()
        self.session.get_proxy_address(proxy)

        self.isp = isp

        self.character = ''
        self.suffixes = ''

    '''
    检测是否为 JSON 数据
    '''
    def __json_check(self, msg):
        try:
            res = msg.json()
            # print(res)
            return res
        except Exception as e:
            print(f'Error: json check {e}')            
            return str(e)

    '''
    检测是否已注册
    '''
    def check_registered(self, character, suffixes):
        # character = 'fdsafdasfdasdfsa'
        self.character = character
        self.suffixes = suffixes
        # print('character: ', self.character)
        domain = '{}.{}'.format(self.character, self.suffixes)

        if self.isp == 'qcloud':
            return self.qcloud(domain) 
        elif self.isp == 'zzidc':
            return self.zzidc(domain)
        elif self.isp == 'westxyz':
            return self.west_search(domain)
        return self.west(domain)    

    '''
    腾讯云
    '''
    def qcloud(self, domain):
        referer_url = 'https://whois.cloud.tencent.com/'
        url = 'https://qcwss.cloud.tencent.com/domain/ajax/newdomain?action=CheckDomainAvailable&from=domain_buy'    

        self.session.set_cookie(referer_url)
        response = self.session.request(url, domain, type = 'post', data = {'DomainName': domain})
        registered, regdate, expdate, err = True, '', '', 0

        try:
            resp = self.__json_check(response)  
            registered = resp['result']['Available'] == False
        except Exception as e:
            print(f'Error: qcloud.com find domain: {domain}, err:{e}') 
            err = 1

        return registered, regdate, expdate, err  

    '''
    西部数码
    '''
    def west(self, domain):
        req_urls = ['https://www.west.xyz', 'https://www.363.hk', 'https://west.cn']
        isp_idx = random.randint(0, len(req_urls) - 1)
        isp_url = req_urls[isp_idx]

        referer_url = '{}/web/whois/whois'.format(isp_url)
        # https://www.west.xyz/en/domain/whois.asp
        url = '{}/web/whois/whoisinfo?domain={}&server=&refresh=0'.format(isp_url, domain)
        # print(url)

        self.session.set_cookie(referer_url)

        response = self.session.request(url, domain)
        registered, regdate, expdate, err = True, '', '', 1

        try:
            # print(response.text)
            resp = self.__json_check(response)  

            if resp['code'] == 200 or resp['code'] == 100:
                registered = resp['regdate'] != ''
                
                if registered:
                    regdate = resp['regdate']
                    expdate = resp['expdate']

                err = 0
        except Exception as e:
            print(f'Error: {isp_url} find domain: {domain}, err:{e}') 

        return registered, regdate, expdate, err    

    '''
    西部数码(search)
    '''
    def west_search(self, domain):
        req_urls = ['https://www.west.xyz']
        # isp_idx = random.randint(0, len(req_urls) - 1)
        isp_url = req_urls[0]
        # https://www.west.xyz/main/domain_do.asp
        url = '{}/main/domain_do.asp'.format(isp_url)
        referer_url = url

        self.session.set_cookie(referer_url)

        domains = domain.split('.')
        
        data = {
            "act": "query",
            "domains": domains[0],
            "suffixs": "." + domains[1]
            }

        response = self.session.request(url, domain, type = 'post', data = data)
        registered, regdate, expdate, err = True, '', '', 1
        # str = "200 ok,a:cxf.pw||9|no|dompw;b:;c:;d:"
        # str = "200 ok,a:fdsafdsafads.com||61|no|domcom;b:;c:;d:"
        # str = "200 ok,a:;b:fei.pw;c:;d:"
        # 200 ok,a:;b:;c:;d:fei.top=4153     
        # print(url)

        try:
            print(response.text)
            str = response.text
            res1 = str.split(',')

            if res1[0] == '200 ok':
                res2 = res1[1].split(';')
                
                if res2[0] != 'a:':
                    res3 = res2[0].split('|')

                    if res3[3] == 'no':
                        registered = False
                        
                err = 0
        except Exception as e:
            print(f'Error: {isp_url} find domain: {domain}, err:{e}') 

        return registered, regdate, expdate, err  

    '''
    Bulk WHOIS (rapidapi)
    https://rapidapi.com/backend_box/api/bulk-whois/
    33 / day | Hard Limit
    '''
    def builk_whois(self, domain):
        url = "https://pointsdb-bulk-whois-v1.p.rapidapi.com/whois"
        querystring = {"domains":domain,"format":"split"}

        headers = {
            'x-rapidapi-host': "pointsdb-bulk-whois-v1.p.rapidapi.com",
            'x-rapidapi-key': "e7cc80a32emsh3af8115155e1edcp11b416jsnbe22a2f028d0"
            }

        response = self.session.request(url, domain, headers=headers, type = 'get', params=querystring)
        print(response.text)
        registered, regdate, expdate, err = True, '', '', 0

        try:
            resp = self.__json_check(response)  

            if 'No match' in resp[domain][0]['0']:
                registered = False
        except Exception as e:
            print(f'Error: builk_whois find domain: {domain}, err:{e}') 
            err = 1

        return registered, regdate, expdate, err  

    '''
    景安 https://zzidc.com
    '''
    def zzidc(self, domain):
        req_urls = ['https://www.zzidc.com', 'https://www.zzidc.hk']
        isp_idx = random.randint(0, len(req_urls) - 1)
        isp_url = req_urls[isp_idx]        
        
        referer_url = '{}/domain/searchDomain?domainName=3&domain={}&tld=.{}'.format(isp_url, self.character, self.suffixes)
        url = '{}/domain/checkDomain'.format(isp_url)
        # print(isp_url)

        self.session.set_cookie(referer_url)
        response = self.session.request(url, domain, type = 'post', data = {'domain': domain})
        registered, regdate, expdate, err = True, '', '', 0

        try:
            resp_sp = response.text.strip('"()').replace('\\"', '"').replace('{', '{"').replace(', ', ',"').replace(':', '":')
            resp_json = json.loads(resp_sp)
            registered = resp_json['val'] == 2
        except Exception as e:
            print(f'Error: {isp_url} find domain: {domain}, err:{e}') 
            err = 1

        return registered, regdate, expdate, err          
