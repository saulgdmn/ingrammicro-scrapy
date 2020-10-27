import requests
import subprocess
import logging
import json

import pandas as pd

from requests.exceptions import ReadTimeout, RequestException
from woocommerce import API
import pickledb

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

log = logging.getLogger(__name__)

categories_db = pickledb.load('categories.db', False)
products_db = pickledb.load('products.db', False)

wcapi = API(
    url="https://www.boardwalktel.com",
    consumer_key="ck_50489c0923c472440db0472e11f4baca25d48369",
    consumer_secret="cs_ab21d88338a4a20edfecab20f391ec1e45e72fe1",
    version="wc/v2",
    query_string_auth=True,
    timeout=30
)


def pull_categories():
    page = 1
    while 1:
        response = wcapi.get(
            endpoint='products/categories',
            params={
                'per_page': 100,
                'page': page
            }
        )

        data = response.json()
        if not data:
            break

        for item in data:
            item_key = item.get('name', None)
            if not item_key:
                continue

            item_value = item.get('id', None)
            if not item_value:
                continue

            item_key = item_key.encode('ascii').decode('ascii')

            categories_db.set(item_key,  item_value)

        page += 1
        categories_db.dump()

    categories_db.dump()

def create_categories(categories):
    for category in categories:
        response = wcapi.post(
            endpoint='products/categories',
            data={
                'name': category,
            }
        )

        if response.status_code != 201:
            continue

        key = response.json().get('name', None)
        if not key:
            continue

        value = response.json().get('id', None)
        if not value:
            continue

        categories_db.set(key, value)


def pull_products():
    page = 1
    while 1:
        response = wcapi.get(
            endpoint='products',
            params={
                'per_page': 100,
                'page': page
            }
        )

        data = response.json()
        if not data:
            break

        for item in data:
            item_key = item.get('sku', None)
            if not item_key:
                continue

            item_value = item.get('id', None)
            if not item_value:
                continue

            item_key = item_key.encode('ascii').decode('ascii')

            products_db.set(item_key, item_value)

        page += 1
        products_db.dump()

    products_db.dump()


def create_or_update_products(products_create, products_update):
    try:
        wcapi.post(
            endpoint='products/batch',
            data={
                'create': products_create,
                'update': products_update
            }
        )
    except ReadTimeout:
        return True
    except RequestException:
        log.warning('Connection error. Retrying..')
        return False

    return True


def get_product_categories(categories):
    if not categories:
        return []

    results = []
    for category in categories:
        if not category:
            continue

        if not categories_db.exists(category):
            continue

        results.append({'id': categories_db.get(category)})

    return results


def get_product_attributes(specs):
    if not specs:
        return []

    results = []
    for sub_spec in specs:
        for spec in sub_spec.get('productSpecifications', []):
            results.append({
                'name': spec.get('key'),
                'options': [spec.get('value')],
                'visible': True
            })
    return results


def get_product_images(images):
    if not images:
        return []

    results = []
    for image in images:
        pass

        if 'no-image-xl.png' in image:
            continue

        results.append({'src': image})

    return results


def find_brand_name(specs):
    if not specs:
        return None

    for sub_spec in specs:
        for spec in sub_spec.get('productSpecifications', []):
            if spec['key'] == 'Brand Name':
                return spec['value']

    return None


def handle_raw_product(item):
    if item.get('stockStatus').replace(' ', '').lower() == 'outofstock':
        return None

    if not item.get('vpn', None):
        return None

    data = {
        'type': 'simple',
        'status': 'publish',
        'name': item.get('title', None),
        'description': item.get('description', None),
        'sku': item.get('vpn', None),
        'regular_price': str(item.get('priceAndStock').get('msrpPrice')),
        'sale_price': str(item.get('priceAndStock').get('dealerPrice')),
        'stock_status': item.get('stockStatus').replace(' ', '').lower(),
        'manage_stock': True,
        'stock_quantity': item.get('priceAndStock').get('availableQuantity', 0),
        'weight': str(item.get('productMeasurement').get('pMeasureWeight', None)),
        'dimensions': {
            'length': str(item.get('productMeasurement').get('pMeasureLength', None)),
            'width': str(item.get('productMeasurement').get('pMeasureWidth', None)),
            'height': str(item.get('productMeasurement').get('pMeasureHeight', None))
        },
        'categories': get_product_categories([item.get('category', None), item.get('subCategory', None)]),
        'attributes': get_product_attributes(item.get('basicSpecifications')),
        'images': get_product_images(item.get('imageGalleryURLHigh', None)),
        'meta_data': [
            {
                'key': '_wpmr_upc',
                'value': str(item.get('upcEan', None)),
            },
            {
                'key': '_wpmr_brand',
                'value': find_brand_name(item.get('basicSpecifications'))
            }
        ]

    }

    return data

def handle_raw_products_dump(filename):

    log.info('Opening {}..'.format(filename))

    total_count = 0
    out_of_stock_count = 0
    wrong_data_count = 0

    create_buffer = []
    update_buffer = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:

            total_count += 1

            if line.endswith('\n'):
                line = line[:-1]

            try:
                item = handle_raw_product(json.loads(line))
                if not item:
                    out_of_stock_count += 1
                    continue
            except Exception as e:
                log.warning('Something has gone wrong: {}'.format(e))
                continue

            if products_db.exists(item.get('sku')):
                item.update({
                    'id': products_db.get(item.get('sku'))
                })
                #update_buffer.append(item)
            else:
                create_buffer.append(item)

            if (len(create_buffer) + len(update_buffer)) == 100:
                log.info('Sending batch data: {}, {}'.format(len(create_buffer), len(update_buffer)))

                while not create_or_update_products(create_buffer, update_buffer):
                    pass

                create_buffer.clear()
                update_buffer.clear()

    log.info('total_count: {}\nout_of_stock_count: {}'.format(total_count, out_of_stock_count))
    log.info('Finished!')


#pull_categories()
#pull_products()

handle_raw_products_dump('22.10.2020-copy.jsonlines')


#with open('products_dump.json') as f:

#    data = json.load(f)
#    print(len(data))
