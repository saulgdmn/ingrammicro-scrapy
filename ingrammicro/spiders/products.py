import os
import re
import json
import logging
from datetime import datetime as dt

import scrapy
from scrapy.http import Request, Response
from scrapy.exceptions import DropItem


class ProductsSpider(scrapy.Spider):
    name = 'products'

    custom_settings = {
        'LOG_FILE': os.path.join(
            'crawls', '{}_{}.log'.format(
                name, dt.now().strftime('%Y-%m-%d'))
        )
    }

    def start_requests(self):

        ingra_products = self.settings.get('INGRA_PRODUCTS')
        existed_data = []
        with open(ingra_products, 'r') as f:
            for r in f:
                data = json.loads(r)
                if not data:
                    continue

                href = data.get('href', None)
                existed_data.append(href.split('=')[1])

        self.logger.info('Count of skus in {} is {}..'.format(ingra_products, len(existed_data)))

        output_filename = list(self.settings.get('FEEDS').attributes.keys())[0]
        with open(output_filename, 'r', encoding='utf8', errors='ignore') as f:
            for r in f:
                product_data = json.loads(r)
                sku = product_data.get('sku', None) or product_data.get('globalSku', None)
                if not sku:
                    continue

                if sku in existed_data:
                    continue

                yield Request(
                    url='https://usa.ingrammicro.com/site/productdetail?id=' + sku,
                    callback=self.parse_event
                )

    def parse_event(self, response: Response):
        m = re.search(r'\{\"productDetail\"\:([^;]+)\)\;', response.text) or \
            re.search(r'\{\"productDetail\"\:([^*]+"isEndUserFavoriteEnabled":true})\);', response.text)

        if not m:
            self.logger.warning('Match error on {}'.format(response.url))

        data = json.loads(m.group(0)[:-2]).get('productDetail', None)
        if not data:
            self.logger.warning('Data error on {}'.format(response.url))

        return data
