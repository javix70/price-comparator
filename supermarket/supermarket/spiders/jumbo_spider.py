
import re
import scrapy
import json
import random

from ..items.jumbo_items import ProductItem
from ..constants import JUMBO_WEB_URL, JUMBO_BASE_URL, JUMBO_PRODUCT_PER_PAGE, USER_AGENTS


class JumboSpider(scrapy.Spider):
    """
    scraping product data from Jumbo's website.
    """
    name = 'jumbo'
    start_urls = [JUMBO_WEB_URL]
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'tenant': 'supermercado',
        'Content-Type': 'application/json'
    }

    def parse(self, response):
        """
        Initial method to be called for the spider.

        Has a 2 step process:
            1. Extract the catalog from the scripts of the response.
            2. Search for the API key in the js files of the response 
        """
        scripts = response.xpath('//script/text()').getall()
        catalog = self._extract_catalog_from_scripts(scripts)
        
        js_files_with_posible_api_key_url = response.css('script[src*="bundle.js"]::attr(src)').getall()

        for script_url in js_files_with_posible_api_key_url:
            headers = self.headers.copy()
            headers['User-Agent'] = random.choice(USER_AGENTS)
            yield scrapy.Request(url=response.urljoin(script_url),
                                callback=self.search_api_key_from_js_file,
                                headers=headers,
                                meta={'catalog': catalog})

    def search_api_key_from_js_file(self, response):
        api_key = self._extract_api_key_from_response(response)
        if api_key:
            self.headers.update({'apiKey': api_key})
            self.logger.info(f"Found API key: {api_key}")

            catalog = response.meta['catalog']
            for item in catalog:
                url = f"{JUMBO_BASE_URL}/v4/products{item['url']}"
                yield self.get_items_from_catalog(url)
        else:
            self.logger.info('API key not found in this js file')

    def get_items_from_catalog(self, url, page=1):
        payload = { 'page': page, 'sc': 11 }

        headers = self.headers.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)

        return scrapy.Request(
            url = url,
            method = 'POST',
            body = json.dumps(payload),
            headers = headers,
            callback = self.parse_items_from_catalog,
            meta={ 'page': page}
        )

    def parse_items_from_catalog(self, response):
        catalog = response.json()
        n_pages = catalog['recordsFiltered'] // JUMBO_PRODUCT_PER_PAGE
        catalog_products = catalog['products']

        for product in catalog_products:
            yield self.get_iformation_product(product['linkText'])

        if n_pages > 0:
            for page in range(1, n_pages + 1):
                yield self.get_items_from_catalog(response.url, page=page)

    def get_iformation_product(self, url):
        url = f"{JUMBO_BASE_URL}/v1/product/{url}"
        payload = { 'sc': 11 }

        headers = self.headers.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)

        return scrapy.Request(
            url = url,
            method = 'GET',
            body = json.dumps(payload),
            headers = headers,
            callback = self.parse_product
        )

    def parse_product(self, response):
        product = response.json()[0]
        item = ProductItem()

        # TODO tengo que analizar los productos que tienen más de un items, al parecer en este caso
        # dado que no son pack porque vienen directamente del catalogo, solo tendrán 1 solo nivel de anidacion
        item['provider'] = 'jumbo'
        item['price'] = product['items'][0]['sellers'][0]['commertialOffer']
        item['brand'] = product['brand']
        item['name'] = product['productName']
        item['gtin13'] = product['items'][0]['ean']

        yield item

    def _extract_api_key_from_response(self, response):
        api_key_pattern = re.compile(r'catalog\s*:\s*\{key\s*:\s*"apiKey"\s*,\s*value\s*:\s*"([^"]+)"\}')
        match = api_key_pattern.search(response.text)

        return match.group(1) if match else None

    def _extract_catalog_from_scripts(self, scripts):
        """
        Parameters:
            scripts (List[str]): list of scripts from the response.
        """
        for script in scripts:
            if 'window.__renderData' in script:
                cleaned_data = script.replace('window.__renderData =', '').strip()
                if cleaned_data.endswith(';'):
                    cleaned_data= cleaned_data[:-1] 

                json_data = json.loads(json.loads(cleaned_data))
                acf = json_data['menu']['acf']
                return acf['items']