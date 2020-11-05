import os
import json
from datetime import datetime as dt

import scrapy
from scrapy import signals
from scrapy.http import Request, Response


class CategoriesSpider(scrapy.Spider):
    name = 'categories'

    custom_settings = {
        'LOG_FILE': os.path.join(
            'crawls', '{}_{}.log'.format(
                name, dt.now().strftime('%Y-%m-%d'))
        )
    }

    deny_categories = [
        'Software',
        ' Sw',
        'Service',
        'Warranties',
        'Warranty',
        'Office Productivity',
        'Training'
    ]

    categories_products_deny = 0
    categories_products = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        self.logger.info('categories_products_deny = {}'.format(self.categories_products_deny))
        self.logger.info('categories_products = {}'.format(self.categories_products))

    def category_is_deny(self, category):
        for x in self.deny_categories:
            if x in category:
                return True
        return False

    def start_requests(self):

        yield Request(
            url="https://usa.ingrammicro.com/_layouts/CommerceServer/IM/MainMenu.asmx/GetProductSubCategory",
            callback=self.parse_subcategories,
            headers={
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "ru,en;q=0.9,uk;q=0.8",
                "content-type": "application/json; charset=UTF-8",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest"
            },
            method="POST",
            body=r"{'contextPath': 'category','fromTab': 'pTab'}"
        )

    def parse_subcategories(self, response: Response):
        for subcategory in json.loads(response.text).get('d', []):
            context_path = subcategory.get('ContextPath', None)
            if not context_path:
                continue

            record_count = subcategory.get('RecordCount', None)
            if not record_count:
                continue

            self.categories_products += record_count
            if self.category_is_deny(context_path):
                self.categories_products_deny += record_count
                continue

            if record_count >= 10000:
                yield Request(
                    url="https://usa.ingrammicro.com/_layouts/CommerceServer/IM/MainMenu.asmx/GetProductSubCategoryVendor",
                    callback=self.parse_subcategories_vendors,
                    headers={
                        "accept": "application/json, text/javascript, */*; q=0.01",
                        "accept-language": "ru,en;q=0.9,uk;q=0.8",
                        "content-type": "application/json; charset=UTF-8",
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "x-requested-with": "XMLHttpRequest"
                    },
                    method="POST",
                    body="{'contextPath': '%s','fromTab': 'pTab'}" % context_path
                )
            else:
                for page in range(1, (record_count // 50) + 2):
                    yield Request(
                        url='https://usa.ingrammicro.com/Site/Search/DoSearch',
                        callback=self.parse_search_page,
                        method='POST',
                        headers={
                            "accept": "*/*",
                            "accept-language": "ru,en;q=0.9,uk;q=0.8",
                            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-origin",
                            "x-requested-with": "XMLHttpRequest"
                        },
                        body="Mode=12&RecordPerPage=50&Term={}&State={}".format(page, context_path),
                    )

    def parse_subcategories_vendors(self, response: Response):
        for result in json.loads(response.text).get('d', []):
            context_path = result.get('ContextPath', None)
            if not context_path:
                continue

            record_count = result.get('RecordCount', None)
            if not record_count:
                continue

            for page in range(1, (record_count // 50) + 2):
                yield Request(
                    url='https://usa.ingrammicro.com/Site/Search/DoSearch',
                    callback=self.parse_search_page,
                    method='POST',
                    headers={
                        "accept": "*/*",
                        "accept-language": "ru,en;q=0.9,uk;q=0.8",
                        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "x-requested-with": "XMLHttpRequest"
                    },
                    body="Mode=12&RecordPerPage=50&Term={}&State={}".format(page, context_path),
                )

    def parse_search_page(self, response: Response):
        for href in response.xpath('//div[@class="row product"]//div/a/@href'):
            yield {
                'href': href.get()
            }
