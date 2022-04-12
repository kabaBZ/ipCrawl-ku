import copy
import requests
import time
from redis import Redis
import json
import random


class FatezeroIP():
    def __init__(self):
        self.url_ip = 'http://proxylist.fatezero.org/proxy.list'
        self.url ="https://ip.jiangxianli.com/?anonymity=2"
        # 构造headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }
        # 测试ip的URL
        self.url_for_test ='http://httpbin.org/ip'
        self.conn = Redis(host='localhost',port=6379)
        self.proxies ={
                'http': '150.109.32.166:80',  #'http://'+
                }
    def scrawl_fatezero_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        url = self.url_ip
        response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
        dic_list = response.text.split('\n')
        for item in dic_list:
            if not item.strip(): continue
            item = json.loads(item)
            ipv4 = item['host']
            port = str(item['port'])
            ip = ipv4 + ':' + port
            ip_list.append(copy.deepcopy(ip))
            print(ip)
        ip_set = set(ip_list)  # 去掉可能重复的ip
        ip_list = list(ip_set)
        print(ip_list)
        return ip_list
    def ip_test(self,url_for_test,ip_info):
        '''
        测试爬取到的ip，测试成功则存入Redis
        '''
        n = 0
        for ip_for_test in ip_info:
            # 设置代理
            proxies ={
            'http': ip_for_test,  #'http://'+
            }
            try:
                response = requests.get(url_for_test,headers=self.headers,proxies=proxies,timeout=5)
                print(response.status_code)
                if response.status_code ==200:
                    print('测试通过:',proxies)
                    x = self.write_to_Redis(ip_for_test)
                    if x == 1:
                        n += 1
                else:
                    print('测试失败:', proxies)
                time.sleep(5)
            except Exception as e:
                print('测试失败:',proxies,e)
                pass
        print('本次向数据库更新数目:',n)
    def write_to_Redis(self,proxies):
        '''
        将测试通过的ip存入Redis
        '''
        ex = self.conn.sadd('Proxies',proxies)
        if ex == 1:
            print('Proxies更新成功')
            return 1
        else:
            print('已存在，未更新。')
            return 0
    def get_random_ip(self):
        '''
        随机取出一个ip
        '''
        useful_proxy_list_bytes = list(self.conn.smembers('Proxies'))
        useful_proxy_list = []
        for bytes in useful_proxy_list_bytes:
            bytes = bytes.decode('utf-8')
            useful_proxy_list.append(bytes)
        print(useful_proxy_list)
        useful_proxy = random.choice(useful_proxy_list)
        proxy ={
        'http' : str(useful_proxy),
        }
        try:
            response = requests.get(self.url_for_test,headers=self.headers,proxies=proxy,timeout=5)
            if response.status_code ==200:
                print('此ip未失效:',useful_proxy)
                return useful_proxy
        except Exception as e:
            print('此ip已失效:',useful_proxy)
            self.conn.srem('Proxies',useful_proxy)
            print('已经从Redis移除')
            self.get_random_ip()
    def proxy_to_redis(self):
        #爬取代理ip1页
        ip_info = self.scrawl_fatezero_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)