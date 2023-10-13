

import re
import scrapy
import json
from pdb import set_trace as st
from ..items.jumbo_items import ProductItem

from pprint import pprint

API_URL = "https://sm-web-api.ecomm.cencosud.com"
TENANT = "catalog/api"
BASE_URL = f"{API_URL}/{TENANT}"
WEB_URL = "https://www.jumbo.cl/"

class JumboSpider(scrapy.Spider):
    name = 'jumbo'
    start_urls = [WEB_URL]
    headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    'Accept': 'application/json, text/plain, */*',
    'tenant': 'supermercado',
    'Content-Type': 'application/json'
    }

    def parse(self, response):
        scripts = response.xpath('//script/text()').getall()
        js_files_with_posible_api_key_url = response.css('script[src*="bundle.js"]::attr(src)').getall()

        for script_url in js_files_with_posible_api_key_url:
            yield scrapy.Request(url=response.urljoin(script_url),
                                callback=self.parse_js_response,
                                headers=self.headers,
                                meta={'scripts': scripts})

    def parse_js_response(self, response):
        api_key_pattern = re.compile(r'catalog\s*:\s*\{key\s*:\s*"apiKey"\s*,\s*value\s*:\s*"([^"]+)"\}')
        match = api_key_pattern.search(response.text)

        if match:
            api_key = match.group(1)
            self.headers.update({'apiKey': api_key})
            self.logger.info(f"Found API key: {api_key}")

            scripts = response.meta['scripts']
            for script in scripts:
                if 'window.__renderData' in script:
                    cleaned_data = script.replace('window.__renderData =', '').strip()
                    if cleaned_data.endswith(';'):
                        cleaned_data= cleaned_data[:-1] 
                    json_data = json.loads(json.loads(cleaned_data))
                    acf = json_data['menu']['acf']
                    items = acf['items']
                    for item in items:
                            url = f"{BASE_URL}/v4/products{item['url']}"
                            yield self.create_post_request(url)
        else:
            self.logger.warning(f"API key not found! for {response.url}")


    def create_post_request(self, url, page=1):
        payload = {
            "page": page,
            "sc": 11
        }

        return scrapy.Request(
            url = url,
            method = 'POST',
            body = json.dumps(payload),
            headers = self.headers,
            callback = self.parse_post_response,
            meta={ 'page': page}
        )

    def parse_post_response(self, response):
        data = response.json()
        n_pages = data['recordsFiltered'] // 40 + 1
        catalog_products = data['products']

        for product in catalog_products:
            yield self.create_post_product_request(product['linkText'])

        if n_pages > 1:
            for page in range(1, n_pages + 1):
                yield self.create_post_request(response.url, page=page)



    def create_post_product_request(self, url):
        url = f"{BASE_URL}/v1/product/{url}"
        payload = {
            "sc": 11
        }
        return scrapy.Request(
            url = url,
            method = 'GET',
            body = json.dumps(payload),
            headers = self.headers,
            callback = self.parse_product
        )

    def parse_product(self, response):
        product = response.json()[0]
        new_product = ProductItem()

        # TODOL tengo que analizar los productos que tienen más de un items, al parecer en este caso
        # dado que no son pack porque vienen directamente del catalogo, solo tendrán 1 solo nivel de anidacion
        new_product['provider'] = 'jumbo'
        new_product['price'] = product['items'][0]['sellers'][0]['commertialOffer']
        new_product['brand'] = product['brand']
        new_product['name'] = product['productName']
        new_product['gtin13'] = product['items'][0]['ean']

        yield new_product