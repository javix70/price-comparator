import scrapy
import uuid
import json

from ..items.lider_items import *

BASE_URL = "https://apps.lider.cl"
TENANT = "supermercado"
BFF = "bff"
BASE_URL = f"{BASE_URL}/{TENANT}/{BFF}"

class LiderSpider(scrapy.Spider):
    name = 'lider'
    base_url = f"{BASE_URL}/categories"
    flowid = str(uuid.uuid4())
    sessionid = str(uuid.uuid4())
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        'Accept': 'application/json, text/plain, */*',
        'tenant': 'supermercado',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.base_url, headers=self.headers, callback=self.parse_categories)

    def parse_categories(self, response):
        data = json.loads(response.text)
        categories = data['categories']

        for category in categories:
            if not category.get('hidden'):
                for path in self.generate_category_paths(category):
                    yield self.create_post_request(path)

    def create_post_request(self, category_path, page=1):
        payload = {
            "page": page,
            "facets": [],
            "sortBy": "",
            "hitsPerPage": 100,
            "categories": category_path
        }
        headers={ 'Content-Type': 'application/json', 'x-channel': 'SOD', 'x-flowid': self.flowid, 'x-sessionid': self.sessionid }
        complete_headers = {**self.headers, **headers} 
        return scrapy.Request(
            url=f"{BASE_URL}/category",
            method='POST',
            body=json.dumps(payload),
            headers=complete_headers,
            callback=self.parse_post_response,
            meta={'category_path': category_path, 'page': page}
        )

    def parse_post_response(self, response):
        data = json.loads(response.text)
        for product in data['products']:
            item = ProductItem()

            for field in ['brand', 'price', 'displayName', 'gtin13']:
                item[field] = product.get(field, None)

            item['provider'] = self.name
            yield item

        if data['nbPages'] > 1 and data['page'] < data['nbPages']:
            next_page = data['page'] + 1
            yield self.create_post_request(response.meta['category_path'], page=next_page)

    
    ## HELPER METHODS only used in this spider
    def generate_category_paths(self, category):
        paths = []
        for subcategory in category['categoriesLevel2']:
            for sub_subcategory in subcategory['categoriesLevel3']:
                path = f"{category['label']}/{subcategory['label']}/{sub_subcategory['label']}"
                paths.append(path)
        return paths