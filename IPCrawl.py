import requests
import random
import time
import json
from lxml import etree
from redis import Redis
from bs4 import BeautifulSoup
import copy
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        }
# 测试ip的URL
url_for_test ='http://httpbin.org/ip'
conn = Redis(host='localhost',port=6379)

def get_random_ip():
    '''
    随机取出一个ip
    '''
    useful_proxy_list_bytes = list(conn.smembers('Proxies'))
    useful_proxy_list = []
    for bytes in useful_proxy_list_bytes:
        bytes = bytes.decode('utf-8')
        useful_proxy_list.append(bytes)
    print(useful_proxy_list)
    useful_proxy = random.choice(useful_proxy_list)
    proxy = {
        'http': str(useful_proxy),
    }
    try:
        response = requests.get(url_for_test, headers=headers, proxies=proxy, timeout=5)
        if response.status_code == 200:
            print('此ip未失效:', useful_proxy)
            return useful_proxy
    except Exception as e:
        print('此ip已失效:', useful_proxy)
        conn.srem('Proxies', useful_proxy)
        print('已经从Redis移除')
        get_random_ip()

#IP66代理
class Ip66Proxy():
    def __init__(self):

        # 爬取代理的URL地址，选择的是66代理
        self.url_ip = 'http://www.66ip.cn/index.html'
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
        #本次更新条数
    def crawl_ip66_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        url = self.url_ip
        response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
        response.encoding = 'gbk'
        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find('div', attrs={'class': 'container'}).find('table')
        for item in soup.find_all('tr')[1:]:
            if item.find_all('td')[0].text.strip() != 'ip':
                ipv4 = item.find_all('td')[0].text.strip()
                port = item.find_all('td')[1].text.strip()
                ip = ipv4 + ':' + port
                ip_list.append(copy.deepcopy(ip))
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
        ip_info = self.crawl_ip66_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)


#Fatezero代理
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
    def crawl_fatezero_ip(self,num):
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
        ip_info = self.crawl_fatezero_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#IP3366代理/云代理
class Ip3366():
    def __init__(self):

        # 爬取代理的URL地址，选择的是3366代理
        self.url_ip ="http://www.ip3366.net/free/?page=1"
        # 构造headers
        self.headers ={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
            'Referer': 'http://www.ip3366.net/free/',
        }
        # 测试ip的URL
        self.url_for_test ='http://httpbin.org/ip'
        self.conn = Redis(host='localhost',port=6379)
        self.proxies ={
                'http': '150.109.32.166:80',  #'http://'+
                }
    def crawl_3366_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        for num_page in range(1,num+1):
            url = self.url_ip + str(num_page)
            response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
            print(response)
            if response.status_code ==200:
                content = response.text
                tree = etree.HTML(content)
                tr_list = tree.xpath('/html/body/div[2]/div/div[2]/table/tbody/tr')
                for tr in tr_list:
                    ipv4 = tr.xpath('./td[1]/text()')[0]
                    port = tr.xpath('./td[2]/text()')[0]
                    ip = ipv4 + ':' + port
                    ip_list.append(copy.deepcopy(ip))
            print(ip_list)
            #不睡封ip
            time.sleep(5)
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
            print(n)
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
        #爬取代理ip5页
        ip_info = self.crawl_3366_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#Jiangxianli代理
class JiangxianliIP():
    def __init__(self):
        # 爬取代理的URL地址，选择的是快代理
        self.url_ip = 'https://ip.jiangxianli.com/?anonymity=2'
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
    def crawl_jiangxianli_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        url = self.url_ip
        response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
        if response.status_code == 200:
            content = response.text
            tree = etree.HTML(content)
            tr_list = tree.xpath('/html/body/div/div[2]/div/div/table/tbody/tr')
            for tr in tr_list:
                try:
                    ipv4 = tr.xpath('./td[1]/text()')[0]
                    port = tr.xpath('./td[2]/text()')[0]
                    ip = ipv4 + ':' + port
                    ip_list.append(copy.deepcopy(ip))
                    print(ip)
                except:
                    pass
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
        #爬取代理ip5页
        ip_info = self.crawl_jiangxianli_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#快代理
class KuaidailiProxy():
    def __init__(self):
        # 爬取代理的URL地址，选择的是快代理
        self.url_ip ="https://www.kuaidaili.com/free/inha/"
        # 构造headers
        self.headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
        # 测试ip的URL
        self.url_for_test ='http://httpbin.org/ip'
        self.conn = Redis(host='localhost',port=6379)
        self.proxies ={
                'http': '150.109.32.166:80',  #'http://'+
                }
        #本次更新条数
    def crawl_kuai_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        for num_page in range(1,num+1):
            url = self.url_ip + str(num_page)
            response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
            print(response)
            if response.status_code ==200:
                content = response.text
                tree = etree.HTML(content)
                tr_list = tree.xpath('/html/body/div[1]/div[4]/div[2]/div[2]/div[2]/table/tbody/tr')
                for tr in tr_list:
                    ipv4 = tr.xpath('./td[1]/text()')[0]
                    port = tr.xpath('./td[2]/text()')[0]
                    ip = ipv4 + ':' + port
                    ip_list.append(copy.deepcopy(ip))
            print(ip_list)
            #不睡封ip
            time.sleep(5)
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
        #爬取代理ip5页
        ip_info = self.crawl_kuai_ip(5)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#Seofangfa方法代理
class SeofangfaProxy():
    def __init__(self):
        self.url_ip = 'https://proxy.seofangfa.com/'
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
    def crawl_seofangfa_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        url = self.url_ip
        response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
        tree = etree.HTML(response.text)
        tr_list = tree.xpath('//tbody/tr')
        for tr in tr_list:
            ipv4 = tr.xpath('./td[1]/text()')[0]
            port = tr.xpath('./td[2]/text()')[0]
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
        #爬取代理ip5页
        ip_info = self.crawl_jiangxianli_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#太阳代理
class TaiyangProxy():
    def __init__(self):
        # 爬取代理的URL地址，选择的是快代理
        self.url_ip ="http://www.taiyanghttp.com/free/page"
        # 构造headers
        self.headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}
        # 测试ip的URL
        self.url_for_test ='http://httpbin.org/ip'
        self.conn = Redis(host='localhost',port=6379)
        self.proxies ={
                'http': '150.109.32.166:80',  #'http://'+
                }
    def crawl_taiyang_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        for num_page in range(1,num+1):
            url = self.url_ip + str(num_page)
            response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
            if response.status_code ==200:
                content = response.text
                tree = etree.HTML(content)
                div_list = tree.xpath('/html/body/section/div[2]/div/div[2]/div')
                for div in div_list:
                    ipv4 = div.xpath('./div[1]/text()')[0]
                    port = div.xpath('./div[2]/text()')[0]
                    ip = ipv4 + ':' + port
                    ip_list.append(copy.deepcopy(ip))
            print(ip_list)
            #不睡封ip
            time.sleep(5)
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
                if response.status_code ==200:
                    print('测试通过:',proxies)
                    x = self.write_to_Redis(ip_for_test)
                    if x == 1:
                        n += 1
                print(response.status_code)
                print('测试失败:', proxies)
            except Exception as e:
                print('测试失败:',proxies,e)
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
        #爬取代理ip5页
        ip_info = self.crawl_taiyang_ip(5)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#yqie代理
class YqieProxy():
    def __init__(self):
        # 爬取代理的URL地址，选择的是yqie代理
        self.url_ip = 'http://ip.yqie.com/ipproxy.htm'
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
    def crawl_yqieIP_ip(self,num):
        '''
        爬取代理ip地址
        '''
        ip_list =[]
        url = self.url_ip
        response = requests.get(url,headers=self.headers,) #,proxies = proxies需要时可设置代理
        response.encoding= 'utf-8'
        tree = etree.HTML(response.text)
        tr_list = tree.xpath('/html/body/div[1]/div[8]/div[4]/table//tr')
        flag = 1
        for tr in tr_list:
            if flag == 1:
                flag = 0
                pass
            else:
                ipv4 = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
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
        ip_info = self.crawl_yqieIP_ip(1)
        #测试ip是否可用并存储至redis
        self.ip_test(self.url_for_test,ip_info)

#站大爷代理
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
get_random_ip()