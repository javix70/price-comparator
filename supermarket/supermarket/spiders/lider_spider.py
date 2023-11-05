import scrapy
import uuid
import json
import random

from ..items.lider_items import ProductItem
from ..constants import USER_AGENTS, LIDER_URL

class LiderSpider(scrapy.Spider):
    name = 'lider'
    base_url = f"{LIDER_URL}/categories"
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'tenant': 'supermercado',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.base_url, headers=self.headers, callback=self.parse_categories)

    def parse_categories(self, response):
        categories = self._extract_categories_from_response(response)
        visible_categories = [cat for cat in categories if not cat.get('hidden')]
        
        paths = [path for category in visible_categories for path in self.generate_category_paths(category)]
        for path in paths:
            yield self.get_iformation_product(path)

    def _extract_categories_from_response(self, response):
        data = response.json()
        return data['categories']

    def get_iformation_product(self, category_path, page=1):
        payload = {
            'page': page,
            'facets': [],
            'sortBy': '',
            'hitsPerPage': 100,
            'categories': category_path
        }
        headers = { 'Content-Type': 'application/json',
                    'User-Agent': random.choice(USER_AGENTS),
                    'x-channel': 'SOD', 'x-flowid': str(uuid.uuid4()),
                    'x-sessionid': str(uuid.uuid4()) }
        complete_headers = { **self.headers, **headers }
    
        return scrapy.Request(
            url=f"{LIDER_URL}/category",
            method='POST',
            body=json.dumps(payload),
            headers=complete_headers,
            callback=self.parse_product,
            meta={'category_path': category_path, 'page': page}
        )

    def parse_product(self, response):
        data = response.json()
        for product in data['products']:
            item = ProductItem()

            item['name'] = product['displayName']
            item['brand'] = product['brand']
            item['price'] = product['price']
            item['gtin13'] = product['gtin13']
            item['provider'] =self.name

            yield item

        if data['nbPages'] > 1 and data['page'] < data['nbPages']:
            next_page = data['page'] + 1
            yield self.get_iformation_product(response.meta['category_path'], page=next_page)

    
    ## HELPER METHODS only used in this spider
    def generate_category_paths(self, category):
        paths = []
        for subcategory in category['categoriesLevel2']:
            for sub_subcategory in subcategory['categoriesLevel3']:
                path = f"{category['label']}/{subcategory['label']}/{sub_subcategory['label']}"
                paths.append(path)
        return paths