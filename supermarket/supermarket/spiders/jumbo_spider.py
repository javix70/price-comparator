

import re
import scrapy
from scrapy_splash import SplashRequest
import uuid
import json
from pdb import set_trace as st
from ..items.lider_items import *

from pprint import pprint

# Esto estando dentro de la pagina de lacteos catergoria
# https://assets.jumbo.cl/json/cms/list-category.json # Lista de Categorias , dentro del array se encuentra la categoria "Lacteos"
# https://sm-web-api.ecomm.cencosud.com/catalog/api/v2/category/facets/lacteos/leches?sc=11 # Filtro barra lateral izquierda de productos
# https://sm-web-api.ecomm.cencosud.com/catalog/api/v4/products/lacteos/leches?page=2&sc=11 # Producto
# El numero de pag, es según el total de productos, maximo 40 por pagina por lo que si es 200/40 = 5 paginas

# Hay este "endoint" de promociones, que queda pendiente de analisis, es probable que no lo necesite dado que si
# Obtengo los productos directamente, puedo obtener el precio de cada uno de ellos desde ahí.
# https://assets.jumbo.cl/json/promotions-v2.json


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
            # no estoy seguro si realmente se requiere splash, me parece que no
            # Cambiar por Request normal despues
            yield SplashRequest(url=response.urljoin(script_url),
                                callback=self.parse_js_response,
                                args={'wait': 2},
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
                    for item in items[:2]:
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
            
        {'Cortes y Partes': ['Carne Molida Especial'],
         'Estado': ['Refrigerado'],
         'Filtros': ['Cortes y Partes', 'Formato', 'Estado', 'Producto Nuevo'],
         'Formato': ['Listo para Cocinar'],
         'Producto Nuevo': ['Producto antiguo'],
         'SkuData': ['{"11491":{"ref_id":"1670575","cart_limit":"12","allow_notes":true,"allow_substitute":true,"measurement_unit":"un","unit_multiplier":1,"promotions":[],"measurement_unit_un":"kg","unit_multiplier_un":0.5,"measurement_unit_selector":false,"release_data":{"date_release":"06-12-2016 '
                     '00:00","date_release_end":"05-01-2017 '
                     '00:00","is_new":false},"promotionData":{"promotionName":"","promotionShortDescription":"","promotionDescription":"","promotionFeature":""}}}'],
         'brand': 'Cuisine & Co',
         'categories': ['/Carnicería/Vacuno/Carne Molida/'],
         'categoriesIds': ['/75/76/80/'],
         'items': [{'images': [{'imageTag': '',
                                 'imageUrl': 'https://jumbo.vtexassets.com/arquivos/ids/652286/Carne-molida-5--grasa-500-g.jpg?v=638183044845570000'}],
                     'itemId': '11491',
                     'measurementUnit': 'un',
                     'name': 'Carne molida 5% grasa 500 g',
                     'referenceId': [{'Key': 'RefId', 'Value': '1670575'}],
                     'sellers': [{'commertialOffer': {'AvailableQuantity': 10000,
                                                     'ListPrice': 5690,
                                                     'Price': 5690,
                                                     'PriceWithoutDiscount': 5690},
                                 'sellerId': '1',
                                 'sellerName': 'Jumbo Chile'}],
                     'unitMultiplier': 1}],
         'linkText': 'carne-molida-5-materia-grasa-500g',
         'productClusters': {'10181': '10181 MiCupon_CarnesVacuno',
                             '1022': 'Google Shopping',
                             '10316': '10316 Especial semana Mexicana',
                             '1059': 'All Products',
                             '10620': '10620 MiCupon_Carnes de vacuno',
                             '1238': '1238 Scraper Carnes',
                             '400': '400 APP Shortcut Carnes',
                             '8008': 'Shortcut - Carnes molidas 8008',
                             '8722': '8722 Shortcut Carnes',
                             '8880': '8880 Top 100 pedidos jumbo.cl'},
         'productId': '11232',
         'productName': 'Carne molida 5% grasa 500 g',
         'productReference': '1670575'}

        if n_pages > 1:
            for page in range(1, n_pages + 1):
                yield self.create_post_request(response.url, page=page)