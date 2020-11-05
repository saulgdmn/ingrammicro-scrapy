import os
import logging
import argparse
import json

import yaml
from requests.exceptions import ReadTimeout, RequestException
from woocommerce import API

import pickledb

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

log = logging.getLogger(__name__)

CATEGORIES_DB = None
PRODUCTS_DB = None

WCAPI = None


def pull_categories():
    page = 1
    while 1:
        response = WCAPI.get(
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

            CATEGORIES_DB.set(item_key, item_value)

        page += 1
        CATEGORIES_DB.dump()

    CATEGORIES_DB.dump()


def pull_products():
    page = 1
    while 1:
        response = WCAPI.get(
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
            PRODUCTS_DB.set(item_key, item_value)

        page += 1
        PRODUCTS_DB.dump()

    PRODUCTS_DB.dump()


def cleanup_products(search_queries):
    to_delete = []
    for query in search_queries:
        page = 1
        while 1:
            response = WCAPI.get(
                endpoint='products',
                params={
                    'per_page': 100,
                    'page': page,
                    'search': query
                }
            )

            data = response.json()
            if not data:
                break

            to_delete += [item.get('id', None) for item in data]
            page += 1

    page = 1
    while 1:
        response = WCAPI.get(
            endpoint='products',
            params={
                'per_page': 100,
                'page': page,
                'min_price': '0.0',
                'max_price': '0.2'
            }
        )

        data = response.json()
        if not data:
            break

        to_delete += [item.get('id', None) for item in data]
        page += 1

    for i in range(0, len(to_delete), 100):
        try:
            WCAPI.post(
                endpoint='products/batch',
                data={
                    'delete': to_delete[i: i + 100]
                }
            )
        except Exception:
            pass

    return len(to_delete)


def get_or_create_categories(categories):
    if not categories:
        return []

    results = []
    for category in categories:
        if not category:
            continue

        if CATEGORIES_DB.exists(category):
            results.append({'id': CATEGORIES_DB.get(category)})
            continue

        response = WCAPI.post(
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

        CATEGORIES_DB.set(key, value)
        results.append({'id': value})

    return results


def create_or_update_products(products_create, products_update):
    try:
        WCAPI.post(
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


def handle_product(item):
    stock_status = item.get('stockStatus', None)
    is_direct_ship = item.get('isDirectShip', False)
    is_direct_ship_orderable = item.get('isDirectShipOrderable', False)

    if stock_status == 'Out Of Stock' and not is_direct_ship and not is_direct_ship_orderable:
        return None

    if not item.get('vpn', None):
        return None

    if not item.get('priceAndStock').get('msrpPrice', None) and not item.get('priceAndStock').get('dealerPrice', None):
        return None

    for x in ['training', 'software', 'warranties', 'warranty']:
        if x in item.get('title', '').lower():
            return None

    data = {
        'type': 'simple',
        'status': 'publish',
        'name': item.get('title', None),
        'description': item.get('description', None),
        'sku': item.get('vpn', None),
        'regular_price': str(item.get('priceAndStock').get('msrpPrice')),
        'sale_price': str(item.get('priceAndStock').get('dealerPrice')),
        'stock_status': 'instock',
        'weight': str(item.get('productMeasurement').get('pMeasureWeight', None)),
        'dimensions': {
            'length': str(item.get('productMeasurement').get('pMeasureLength', None)),
            'width': str(item.get('productMeasurement').get('pMeasureWidth', None)),
            'height': str(item.get('productMeasurement').get('pMeasureHeight', None))
        },
        'categories': get_or_create_categories([item.get('category', None), item.get('subCategory', None)]),
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

    if item.get('priceAndStock').get('availableQuantity', None):
        data.update({
            'manage_stock': True,
            'stock_quantity': item.get('priceAndStock').get('availableQuantity', None)
        })

    return data


def handle_filename(fn, batch_len, update_if_exist):
    log.info('Starting uploading "{}" with batch_len is {}..'.format(fn, batch_len))

    total_count = 0

    create_buffer = []
    update_buffer = []

    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:

            if line.endswith('\n'):
                line = line[:-1]

            try:
                item = handle_product(json.loads(line))
                if not item:
                    continue
            except Exception as e:
                log.warning('Something has gone wrong: {}'.format(e))
                continue

            if PRODUCTS_DB.exists(item.get('sku')):
                if not update_if_exist:
                    continue

                item.update({
                    'id': PRODUCTS_DB.get(item.get('sku'))
                })
                update_buffer.append(item)
            else:
                create_buffer.append(item)

            if (len(create_buffer) + len(update_buffer)) == batch_len:
                total_count += batch_len

                log.info('Sending batch data, to create - {}, to update - {}, total - {})'.format(
                    len(create_buffer), len(update_buffer), total_count))

                while not create_or_update_products(create_buffer, update_buffer):
                    pass

                create_buffer.clear()
                update_buffer.clear()

    log.info('Finished!')


def run():
    global CATEGORIES_DB, PRODUCTS_DB, WCAPI

    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', action='store', required=True)
    parser.add_argument('--config', action='store', required=True)
    parser.add_argument('--timeout', action='store', default='10')
    parser.add_argument('--batch_len', action='store', default='10')
    parser.add_argument('--update_if_exist', action='store_true')
    parser.add_argument('--pull_categories', action='store_true')
    parser.add_argument('--pull_products', action='store_true')
    parser.add_argument('--cleanup_products', action='store_true')

    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.load(f, yaml.BaseLoader)

    CATEGORIES_DB = pickledb.load(os.path.join('imports', '%s_categories.db' % config.get('name')), False)
    PRODUCTS_DB = pickledb.load(os.path.join('imports', '%s_products.db' % config.get('name')), False)

    WCAPI = API(
        url=config.get('url'),
        consumer_key=config.get('consumer_key'),
        consumer_secret=config.get('consumer_secret'),
        version="wc/v2",
        query_string_auth=True,
        timeout=int(args.timeout)
    )

    if args.pull_categories:
        log.info('Pulling categories from website..')
        pull_categories()
        log.info('Count of pulled categories: {}'.format(len(CATEGORIES_DB.getall())))

    if args.pull_products:
        log.info('Pulling products from website..')
        pull_products()
        log.info('Count of pulled products: {}'.format(len(PRODUCTS_DB.getall())))

    '''
    handle_filename(
        fn=args.filename,
        batch_len=int(args.batch_len),
        update_if_exist=args.update_if_exist
    )
    '''

    if args.cleanup_products:
        log.info('Cleanup products..')
        deleted_products_count = cleanup_products(['software', 'license', 'training'])
        log.info('Count of deleted products: {}'.format(deleted_products_count))


if __name__ == '__main__':
    run()

# PRODUCTS_COUNT =  658 876
# SUBCATEGORIES_PRODUCT_COUNT =  435 891


# total_count: 249694
# out_of_stock_count: 223579

# 48 701 at 23:29
