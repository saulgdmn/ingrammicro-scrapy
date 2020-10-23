BOT_NAME = 'ingrammicro'

SPIDER_MODULES = ['ingrammicro.spiders']
NEWSPIDER_MODULE = 'ingrammicro.spiders'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0
LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    'ingrammicro.pipelines.IngrammicroPipeline': 300,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 700,
    'scrapy_selenium.SeleniumMiddleware': 800,
}

FEED_EXPORT_ENCODING = 'utf-8'

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = 'chromedriver.exe'
SELENIUM_DRIVER_ARGUMENTS = ['-headless']

ROTATING_PROXY_LIST = [
    'https://daveklien:6A1IVqkat9uTiBMwnAl@192.241.70.45:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@192.241.70.136:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@198.245.79.112:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@23.250.110.9:2089',

    'https://daveklien:6A1IVqkat9uTiBMwnAl@23.250.89.78:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.159.106:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.173.41:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.145.86:2089',

        ]
'''
'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.196.122:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.210.41:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.215.10:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.227.171:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.177.88:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.181.50:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.186.63:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.196.51:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.81.127:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.184.185:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.36.114:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.71.183:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.100.177:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.224.62:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.229.93:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.140.173:2089',
    'https://daveklien:6A1IVqkat9uTiBMwnAl@104.144.253.136:2089',

]
'''

USER_AGENTS = [
    'Mozilla/5.0 (iPad; CPU OS 8_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12D508 Safari/600.1.4',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
    'Mozilla/5.0 (iPad; CPU OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53',
    'Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFTHWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/7.1.6 Safari/537.85.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2',
    'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/45.0.2454.68 Mobile/12H321 Safari/600.1.4',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4',
    'Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53',
    'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; TNJB; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; ARM; Trident/7.0; Touch; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MDDCJS; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4',
    'Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFASWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/7.0.55539 Mobile/12H321 Safari/600.1.4',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',

]