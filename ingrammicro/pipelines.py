from scrapy.exceptions import DropItem

from woocommerce import API
from requests.exceptions import ReadTimeout

wcapi = API(
    url="https://www.boardwalktel.com",
    consumer_key="ck_dd4e1dfc7b8b6971b40ae03eb327868195545e7f",
    consumer_secret="cs_eae8e34a48e7b1961cae000103f4e752a2cd1ec8",
    version="wc/v3",
    query_string_auth=True,
    timeout=5
)


def get_categories(categories):
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


def retrieve_product_attributes(specs):
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


def push_product(data):
    try:
        response = wcapi.post(
            endpoint='products',
            data=data
        )
    except ReadTimeout:
        return True

    if response.status_code != 201:
        raise DropItem('Pushing failed: {}'.format(response.text))
    else:
        return True


def find_brand_name(specs):
    if not specs:
        return None
    for sub_spec in specs:
        for spec in sub_spec.get('productSpecifications', []):
            if spec['key'] == 'Brand Name':
                return spec['value']

    return None


class IngrammicroPipeline:
    def process_item(self, item, spider):

        return item

        if item.get('stockStatus').replace(' ', '').lower() != 'instock':
            raise DropItem('Out Of Stock')

        if is_product_duplicated(item.get('vpn')):
            raise DropItem('Duplicated')

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
            'categories': get_categories([item.get('category', None), item.get('subCategory', None)]),
            'attributes': retrieve_product_attributes(item.get('basicSpecifications')),
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

        push_product(data)
        return data