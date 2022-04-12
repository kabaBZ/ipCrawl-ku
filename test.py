import IPCrawl

#实例化
Ip66 =IPCrawl.Ip66Proxy()
IP3366 = IPCrawl.Ip3366
Jiangxiangli = IPCrawl.JiangxianliIP
Fatezero = IPCrawl.FatezeroIP
Kuaidaili = IPCrawl.KuaidailiProxy
Seofangfa = IPCrawl.SeofangfaProxy
Taiyang = IPCrawl.TaiyangProxy
Yqie = IPCrawl.YqieProxy
Zdaye = IPCrawl.ZdayeProxy
#更新ip
Taiyang.proxy_to_redis()
#取ip
IPCrawl.get_random_ip()

