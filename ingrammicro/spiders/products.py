import re
import json

import scrapy
from scrapy.http import Request, Response
from scrapy.exceptions import DropItem


class ProductsSpider(scrapy.Spider):
    name = 'products'

    def start_requests(self):

        filename = self.settings.get('INGRA_PRODUCTS', None)
        if not filename:
            return

        with open(filename, 'r', encoding='utf8', errors='ignore') as f:
            for x in json.load(f):
                href = x.get('href', None)
                if not href:
                    continue

                yield Request(
                    url='https://usa.ingrammicro.com' + href,
                    callback=self.parse_event
                )

    def parse_event(self, response: Response):
        m = re.search(r'\{\"productDetail\"\:([^;]+)\)\;', response.text) or \
            re.search(r'\{\"productDetail\"\:([^&]+)\)\;', response.text) or \
            re.search(r'\{\"productDetail\"\:([^*]+"isEndUserFavoriteEnabled":true})\);', response.text)

        if not m:
            raise DropItem('Match error')

        data = json.loads(m.group(0)[:-2]).get('productDetail', None)
        if not data:
            raise DropItem('Data error')

        return data