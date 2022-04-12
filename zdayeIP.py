import copy
import time
from redis import Redis
import requests
from lxml import etree
import random
from copy import deepcopy

class ZdayeProxy():
    def __init__(self):

        self.main_url = 'https://www.zdaye.com/dayProxy/1.html'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }
        self.ip_list = []
        self.url_for_test ='http://httpbin.org/ip'
        #第二页ipURL
        self.ip2_url_list = []
        self.url_list = []
        self.conn = Redis(host='localhost',port=6379)
        self.proxies ={
                'http': '47.108.234.147:8088',  #'http://'+
                }
    def get_detail_url(self,url):
        x = 0
        detail_url_list = []
        main_data = requests.get(url,headers = self.headers)#,proxies = proxies
        main_data.encoding = 'gbk'
        tree = etree.HTML(main_data.text)
        detail_url_xpath = tree.xpath('//div[@class = "thread_item"]//h3/a/@href')
        for xpath in detail_url_xpath:
            x += 1
            detail_url_list.append(copy.deepcopy('https://www.zdaye.com' + xpath))
            self.url_list.append(copy.deepcopy('https://www.zdaye.com' + xpath))
            if x == 4 :
                break
        return detail_url_list
    def parse_detail_url(self,url):
        detail_url_2 = url.split('.html')[0]+'/2'+'.html'
        self.url_list.append(copy.deepcopy(detail_url_2))
    def parse_ip(self,url):
        data = requests.get(url ,headers = self.headers)#,proxies = proxies
        data.encoding = 'gbk'
        print(data.text)
        tree = etree.HTML(data.text)
        tr_list = tree.xpath('/html/body/div[3]/div/div[2]/div/div[5]/table//tr')
        for tr in tr_list:
            ipv4 = tr.xpath('./td[1]/text()')[0]
            port = tr.xpath('./td[2]/text()')[0]
            ip = ipv4 + ':' + port
            self.ip_list.append(copy.deepcopy(ip))
            print(ip)
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
                if response.status_code ==200:
                    print('测试通过:',proxies)
                    x = self.write_to_Redis(ip_for_test)
                    if x == 1:
                        n += 1
            except Exception as e:
                print('测试失败:',proxies)
                continue
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
        self.get_random_ip()
        for url in self.get_detail_url(self.main_url):
            self.parse_detail_url(url)
        # for url in self.url_list:
        #     self.parse_ip(url)
        #     time.sleep(5)
        self.parse_ip(self.url_list[0])
        print(self.ip_list)
        self.ip_test(self.url_for_test,self.ip_list)
