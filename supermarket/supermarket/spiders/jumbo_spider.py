

import scrapy
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
            
            for script in scripts:
                if 'window.__renderData' in script:
                    cleaned_data = script.replace('window.__renderData =', '').strip()
                    if cleaned_data.endswith(';'):
                        cleaned_data = cleaned_data[:-1]

                    # - active: bool                                          True
                    # - banner: Dict
                    #     - active: bool                                      False
                    #     - end_date: str                                     ''
                    #     - image_desktop: bool                               False
                    #     - image_mobile: bool                                False
                    #     - start_date: str                                   ''
                    #     - title: str                                        ''
                    #     - url: str                                          ''
                    # - items: List
                    #     - 0: Dict
                    #         - active: bool                                  True
                    #         - items: List
                    #             - 0: Dict
                    #                 - active: bool                          True
                    #                 - title: str                            'Bebidas en Lata e Individuales'
                    #                 - url: str                              '/bebidas-aguas-y-jugos/bebidas-gaseosas/bebidas-en-lata-e-individuales'
                    #             - 1: Dict
                    #                 - active: bool                          True
                    #                 - title: str                            'Bebidas Light o Zero Azúcar'
                    #                 - url: str                              '/bebidas-aguas-y-jugos/bebidas-gaseosas/bebidas-light-o-zero-azucar'
                    #             - 2: Dict
                    #                 - active: bool                          True
                    #                 - title: str                            'Bebidas Regulares'
                    #                 - url: str                              '/bebidas-aguas-y-jugos/bebidas-gaseosas/bebidas-regulares'
                    #             - 3: Dict
                    #                 - active: bool                          True
                    #                 - title: str                            'Bebidas Retornables'
                    #                 - url: str                              '/bebidas-aguas-y-jugos/bebidas-gaseosas/bebidas-retornables'
                    #         - title: str                                    'Bebidas'
                    #         - url: str                                      '/bebidas-aguas-y-jugos/bebidas-gaseosas'

                    # Los elementos más importantes en este caso, sería title y url, para poder generar la url de cada categoria
                    # quizá entrando a cada url de categoría podría obtener un endpoint interesante, como api

                    json_data = json.loads(json.loads(cleaned_data))
                    # dict_keys(['slug', 'acf', 'updateTime'])
                    
                    acf = json_data['menu']['acf']
                    # dict_keys(['items', 'fixed_categories', 'offers', 'campaigns'])
                    #  en donde fixed_categories son la categoria principal, y items son las subcategorias, offer y campaingm, ignorar por ahora.

                    items = json_data['menu']['acf']['items']
                    for item in items:
                         url = f"{BASE_URL}/v4/products{item['url']}"
                         yield self.create_post_request(url)
                         
                    # https://sm-web-api.ecomm.cencosud.com/catalog/api/v4/products/bebidas-aguas-y-jugos/bebidas-gaseosas/bebidas-en-lata-e-individuales?page=1&sc=11 # Producto
                    # armar la url a partir de la categoria
                    # BASE_URL/v4/products/{category}/{sub_category}/{sub_sub_category}?page={page}&sc=11

                    break
                    
                    # - recordsFiltered: int                                 (valor no proporcionado)
                    # - operator: str                                        'and'
                    # - products: List
                    #     - 0: Dict
                    #         - productId: str                               '44040'
                    #         - productName: str                            'Pack 6 un. Bebida Coca Cola Sin Azúcar Lata 350 cc'
                    #         - brand: str                                  'Coca-Cola'
                    #         - SkuData: List
                    #             - 0: str                                  (valor JSON serializado proporcionado)
                    #         - productReference: str                       '713795-PAK'
                    #         - categoriesIds: List
                    #             - 0: str                                  '/189/190/893/'
                    #         - categories: List
                    #             - 0: str                                  '/Bebidas, Aguas y Jugos/Bebidas Gaseosas/Bebidas en Lata e Individuales/'
                    #         - productClusters: Dict
                    #             - 164: str                                'flag libre de azucar añadida'
                    #             - 749: str                                '749 FDM Junio + ciclo 3'
                    #             - 1002: str                               'Cuando Calienta el Sol'
                    #             - 1022: str                               'Google Shopping'
                    #         - Evento: List
                    #             - 0: str                                  'Cyber'
                    #         - linkText: str                               'pack-bebida-coca-cola-zero-6-unid-350-cc-c-u'
                    #         - items: List
                    #             - 0: Dict
                    #                 - itemId: str                         '43762'
                    #                 - name: str                           'Pack 6 un. Bebida Coca Cola Sin Azúcar Lata 350 cc'
                    #                 - unitMultiplier: int                 1
                    #                 - measurementUnit: str                'un'
                    #                 - images: List
                    #                     - 0: Dict
                    #                         - imageUrl: str               'https://jumbo.vtexassets.com/arquivos/ids/698794/Pack-6-un-Bebida-Coca-Cola-Sin-Azucar-Lata-350-cc.jpg?v=638271126548670000'
                    #                         - imageTag: str               ''
                    #                 - referenceId: List
                    #                     - 0: Dict
                    #                         - Key: str                    'RefId'
                    #                         - Value: str                  '713795-PAK'
                    #                 - sellers: List
                    #                     - 0: Dict
                    #                         - sellerId: str               '1'
                    #                         - sellerName: str             'Jumbo Chile'
                    #                         - commertialOffer: Dict
                    #                             - Price: int              4290
                    #                             - ListPrice: int          5990
                    #                             - PriceWithoutDiscount: int 5990
                    #                             - AvailableQuantity: int  10000
                    #         - Filtros: List
                    #             - 0: str                                  'Producto Nuevo'
                    #             - 1: str                                  'Evento'
                    #         - Producto Nuevo: List
                    #             - 0: str                                  'Producto antiguo'

                    # https://sm-web-api.ecomm.cencosud.com/catalog/api/v4/products/bebidas-aguas-y-jugos/bebidas-gaseosas/bebidas-en-lata-e-individuales?page=1&sc=11 # Producto\
                
    def create_post_request(self, url, page=1):
        payload = {
            "page": page,
            "sc": 11,
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
         perejil = response
         st()
         perejil = 'perejil'