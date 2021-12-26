import json
import random
from enum import Enum

import requests

from client import Client

class ISP(Enum):
    WEST = 'west'

class Whois(object):

    def __init__(self, isp = 'west'):
        self.session = Client()
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

        return self.west(domain)    

    '''
    腾讯云
    '''
    def qcloud(self, domain):
        referer_url = 'https://whois.cloud.tencent.com/'
        url = 'https://qcwss.cloud.tencent.com/domain/ajax/newdomain?action=CheckDomainAvailable&from=domain_buy'    

        self.session.set_cookie(referer_url)
        response = self.session.proxy_request(url, domain, type = 'post', data = {'DomainName': domain})
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
        # print(url, msg.text)

        self.session.set_cookie(referer_url)

        response = self.session.proxy_request(url, domain)
        registered, regdate, expdate, err = True, '', '', 0

        try:
            resp = self.__json_check(response)  

            registered = resp['regdate'] != None
            regdate = resp['regdate']
            expdate = resp['expdate']

            if regdate == None:
                regdate = ''
                expdate = ''
        except Exception as e:
            print(f'Error: {isp_url} find domain: {domain}, err:{e}') 
            err = 1

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

        response = self.session.proxy_request(url, domain, headers=headers, type = 'get', use_proxy = False, params=querystring)
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
        response = self.session.proxy_request(url, domain, type = 'post', data = {'domain': domain})
        registered, regdate, expdate, err = True, '', '', 0

        try:
            resp_sp = response.text.strip('"()').replace('\\"', '"').replace('{', '{"').replace(', ', ',"').replace(':', '":')
            resp_json = json.loads(resp_sp)
            registered = resp_json['val'] == 2
        except Exception as e:
            print(f'Error: {isp_url} find domain: {domain}, err:{e}') 
            err = 1

        return registered, regdate, expdate, err          
