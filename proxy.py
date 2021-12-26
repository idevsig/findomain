import requests,json

class Proxy(object):

    def __init__(self):
        self.filename = 'proxy.log'
        self.clear_proxy()

    def clear_proxy(self):
        open(self.filename, 'w').truncate()

    def write_proxy(self, ip_pools):
        for ip in ip_pools:
            # 写入文件
            with open(self.filename, 'a') as file_object:
                file_object.write(f"{ip}\n")     

    def get_xiladaili(self):
        url = 'http://www.xiladaili.com/api/?uuid=af075aa6d91749f2a7ac1e9dfc3205ef&num=100&place=%E4%B8%AD%E5%9B%BD&protocol=1&sortby=0&repeat=1&format=3&position=1'
        response = requests.get(url)
        return response.text.split(' ')

    def get_jiangxianli(self):
        url = 'https://ip.jiangxianli.com/api/proxy_ips'
        response = requests.get(url)
        ip_pools = []

        for page in range(1, response.json()['data']['last_page']):
            req_url = '{}?page={}'.format(url, page)
            # print(req_url)
            response = requests.get(req_url)
            
            for item in response.json()['data']['data']:
                # print(item['ip'])
                proxy_ip = '{}:{}'.format(item['ip'], item['port'])
                ip_pools.append(proxy_ip)            

        # print(ip_pools, len(ip_pools))
        return ip_pools

    def get_fate0(self):
        url = 'https://ghproxy.com/https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'
        response = requests.get(url)
        resp_json = response.text.split('\n')
        # print(resp_json)

        ip_pools = []
        for s in resp_json:
            if s == "":
                continue

            try:
                item = json.loads(s)
                proxy_ip = '{}:{}'.format(item['host'], item['port'])
                ip_pools.append(proxy_ip)   
            except Exception as e:
                print(f"Error: get_fate0 {e} {s}")

        # print(ip_pools, len(ip_pools))
        return ip_pools
       