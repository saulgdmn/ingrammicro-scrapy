import requests
import re
import json


from pprint import pprint

from woocommerce import API

wcapi = API(
    url="https://www.boardwalktel.com",
    consumer_key="ck_dd4e1dfc7b8b6971b40ae03eb327868195545e7f",
    consumer_secret="cs_eae8e34a48e7b1961cae000103f4e752a2cd1ec8",
    version="wc/v3",
    query_string_auth=True,
    timeout=60
)


def is_product_duplicated(vpn):
    result = wcapi.get(
        endpoint='products',
        params={
            'sku': vpn
        }
    )

    if not result.json():
        return False
    else:
        return True

def get_category(category):
    result = wcapi.get(
        endpoint='products/categories',
        params={
            'search': category
        },
        timeout=0
    )

    pprint(result.json())

'''
with open('19-10-2020-2.jsonlines') as f:
    result = []
    for line in f.readlines():
        result.append(json.loads(line))

    response = wcapi.post(endpoint='products/batch', data={'create': result})
    pprint(response.json())

'''



#print(is_product_duplicated('VA2446MH-LED'))
#get_category('Portable Computers')

'''
response = requests.get(url="https://usa.ingrammicro.com/site/productdetail?id=A300-8AW117#")

m = re.search(r'\{\"productDetail\"\:([^;]+)\)\;', response.text)
product_detail = json.loads(m.group(0)[:-2]).get('productDetail')

response_ = wcapi.post(
    endpoint='products',
    data={
        'name': product_detail.get('title', None),
        'description': product_detail.get('description', None),
        'sku': product_detail.get('sku', None),
        'regular_price': str(product_detail.get('priceAndStock').get('msrpPrice')),
        'stock_status': product_detail.get('stockStatus').replace(' ', '').lower(),
        'related_ids': product_detail.get(''),
        'images': [{'src': x} for x in product_detail.get('imageGalleryURLHigh', [])],

    }
)

pprint(response_.request.body)

pprint(response_.text)
'''