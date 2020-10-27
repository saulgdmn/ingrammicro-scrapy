import json

import scrapy
from scrapy.http import Request, Response


class CategoriesSpider(scrapy.Spider):
    name = 'categories'

    deny_categories = [
        'Software',
        ' Sw',
        'Service',
        'Warranties',
        'Office Productivity'
    ]

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

            if self.category_is_deny(context_path):
                continue

            yield Request(
                url="https://usa.ingrammicro.com/_layouts/CommerceServer/IM/MainMenu.asmx/GetProductSubCategory",
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

    def parse_subcategories_vendors(self, response: Response):
        for result in json.loads(response.text).get('d', []):
            context_path = result.get('ContextPath', None)
            if not context_path:
                continue

            record_count = result.get('RecordCount', 0)
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
