import requests
import json
import subprocess

from pprint import pprint
from requests.exceptions import ReadTimeout
from woocommerce import API

wcapi = API(
    url="https://www.univold.com",
    consumer_key="ck_5466b6b190dae77021242be909655b4507aad812",
    consumer_secret="cs_2f7a0e9e4efaa717fc54db090c64248165c72de5",
    version="wc/v3",
    query_string_auth=True,
    timeout=3
)

def create_categories(categories):
    result = []
    for category in categories:
        if not category:
            continue

        response = wcapi.get(
            endpoint='products/categories',
            params={
                'search': category,
                'per_page': 1
            }
        )

        if not response.json():
            response = wcapi.post(
                endpoint='products/categories',
                data={
                    'name': category,
                }
            )

            category_id = response.json().get('id', None)
            if not category_id:
                continue

            result.append({'id': category_id})
        else:
            category_id = response.json()[0].get('id', None)
            if not category_id:
                continue

            result.append({'id': category_id})

    return result


def is_product_duplicated(vpn):
    result = wcapi.get(
        endpoint='products',
        params={
            'sku': vpn
        }
    )

    if not result.json():
        return False

    return result.json()


def get_product_attributes(specs):
    result = []
    if not specs:
        return []
    for sub_spec in specs:
        for spec in sub_spec.get('productSpecifications', []):
            result.append({
                'name': spec.get('key'),
                'options': [spec.get('value')],
                'visible': True
            })
    return result


def push_products_batch(items):
    try:
        response = wcapi.post(
            endpoint='products/batch',
            data={
                'create': items
            }
        )
    except ReadTimeout:
        return True

    print(response.status_code, response.text)
    return True


def find_brand_name(specs):
    if not specs:
        return None
    for sub_spec in specs:
        for spec in sub_spec.get('productSpecifications', []):
            if spec['key'] == 'Brand Name':
                return spec['value']

    return None


def handle_row(item):
    if item.get('stockStatus').replace(' ', '').lower() == 'outofstock':
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
        #'categories': get_categories([item.get('category', None), item.get('subCategory', None)]),
        'attributes': get_product_attributes(item.get('basicSpecifications')),
        'images': [{'src': x} for x in item.get('imageGalleryURLHigh', []) if 'no-image-xl.png' not in x],
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


with open('22.10.2020-copy-prepared.jsonlines', 'r', encoding='utf-8') as f:
    data = json.load(f)

    for x in range(4):
        push_products_batch(data[x * 100:(x + 1) * 100])

'''
results = []
with open('22.10.2020-copy.jsonlines', 'r', encoding='utf8') as f:
    for line in f.readlines():
        d = handle_row(json.loads(line))
        if not d:
            continue

        results.append(d)

with open('22.10.2020-copy-prepared.jsonlines', 'w', encoding='utf-8') as f:
    f.write(json.dumps(results))
'''