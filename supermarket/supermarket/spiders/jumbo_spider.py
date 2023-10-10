

import re
import scrapy
import requests
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
                    for item in items[:2]: # TODO: remover el slice
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
        data = json.loads(response.text)
        n_pages = data['recordsFiltered'] // 40 + 1
        products = data['products']
        new_product = ProductItem()

        key_convert = {'brand': 'brand', 'items': 'items', 'productName': 'name'}
        for product in products:
            for key, value in product.items():
                if key in key_convert:
                    new_product[key_convert[key]] = value
            new_product['provider'] = self.name
            st()
            yield new_product

        if n_pages > 1:
            for page in range(1, n_pages + 1):
                yield self.create_post_request(response.url, page=page)