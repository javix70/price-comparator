import scrapy
import uuid
import json

from ..items import *

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

    # Obtener todas las categorias
    # categories: List[Dict]
    # - label: str
    # - icon: str (URL)
    # - image: str (URL)
    # - campaignTag: str
    # - textColor: str
    # - selectedTextColor: str
    # - indicatorColor: str
    # - special: bool
    # - hidden: bool
    # - categoriesLevel2: List[Dict]
    #     - label: str
    #     - categoriesLevel3: List[Dict]
    #         - label: str
    #         - hidden: bool
    #         - filters: List[str]
    def parse_categories(self, response):
        data = json.loads(response.text)
        categories = data['categories']
        
        for category in categories:
            if not category.get('hidden'):
                for path in self.generate_category_paths(category):
                    yield self.create_post_request(path)

    # Creacion de request POST para obtener productos
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

    # Procesado de respuesta POST <productos>Dict
      # - facets: Dict                                          {'filters.Marca': {'El Buen Corte': 34, 'id': 'marca'}}
      #     - filters.Marca: Dict                               {'El Buen Corte': 34, 'id': 'marca'}
      #         - El Buen Corte: int                            34
      #         - id: str                                       'marca'
      # - hasVariants: bool                                     False
      # - nbHits: int                                           34
      # - nbPages: int                                          1
      # - page: int                                             1
      # - priceRange: Dict                                      {'max': 19990, 'min': 2590}
      #     - max: int                                          19990
      #     - min: int                                          2590
      # - products: List[Dict]                                  [{'ID': 'PROD_695853', 'attributes': {...}, ...}]
      #     - ID: str                                           'PROD_695853'
      #     - attributes: Dict                                  {'contentUom': '500 gr', ...}
      #         - contentUom: str                               '500 gr'
      #         - defaultQuantity: str                          '1'
      #         - department: str                               '93'
      #         - sellerType: str                               '1P'
      #         - soldByWeight: str                             'false'
      #         - volumetricWeight: str                         '1'
      #     - available: bool                                   True
      #     - brand: str                                        'El Buen Corte'
      #     - categorias: List[str]                             ['Carnes y Pescados/Todas las Carnes/Cortes Clásicos', ...]
      #     - defaultQuantity: int                              1
      #     - description: str                                  'Carne Molida de Vacuno 4% grasa'
      #     - destacado: bool                                   False
      #     - discount: int                                     0
      #     - displayName: str                                  'Carne Molida de Vacuno 4% grasa, 500 gr'
      #     - gtin13: str                                       '0400005187049'
      #     - images: Dict                                      {'availableImages': [], 'defaultImage': 'https://...', ...}
      #         - availableImages: List                         []
      #         - defaultImage: str (URL)                       'https://images.lider.cl/wmtcl?source=url[file:/productos/695853a.jpg]&scale=size[180x180]&sink'
      #         - largeImage: str (URL)                         'https://images.lider.cl/wmtcl?source=url[file:/productos/695853a.jpg]&scale=size[2000x2000]&sink'
      #         - mediumImage: str (URL)                        'https://images.lider.cl/wmtcl?source=url[file:/productos/695853a.jpg]&scale=size[450x450]&sink'
      #         - smallImage: str (URL)                         'https://images.lider.cl/wmtcl?source=url[file:/productos/695853a.jpg]&scale=size[180x180]&sink'
      #     - isMKP: bool                                       False
      #     - itemNumber: str                                   '518704'
      #     - keyword: List[str]                                ['Carnes', 'Clean_Categories_W39']
      #     - leadTime: int                                     0
      #     - longDescription: str                              ''
      #     - makePublic: bool                                  True
      #     - max: int                                          99
      #     - nutritionalInformation: Dict                      {'ingredients': '', 'nutritionalAttributes': [], ...}
      #         - ingredients: str                              ''
      #         - nutritionalAttributes: List                   []
      #         - seals: List                                   []
      #         - servingSize: str                              ''
      #         - servingsPerContainer: int                     0
      #     - posicion: int                                     0
      #     - price: Dict                                       {'BasePricePerUm': 'Precio x Kg : $10.580', ...}
      #         - BasePricePerUm: str                           'Precio x Kg : $10.580'
      #         - BasePriceReference: int                       5290
      #         - BasePriceSales: int                           5290
      #         - BasePriceTLMC: int                            0
      #         - packPrice: int                                10000
      #         - packSize: int                                 2
      #     - sites: List[str]                                  ['gr.walmart.cl']
      #     - sku: str                                          '695853'
      #     - specifications: List[Dict]                        [{'name': 'Descripción', 'order': 1, 'value': 'Carne Molida de Vacuno 4% grasa'}, ...]
      #         - name: str                                     'Descripción'
      #         - order: int                                    1
      #         - value: str                                    'Carne Molida de Vacuno 4% grasa'
      #     - tags: Dict                                        {'attributeTags': [], 'campaignTags': [], 'deliveryTags': []}
      #         - attributeTags: List                           []
      #         - campaignTags: List                            []
      #         - deliveryTags: List                            []
      #     - vendorId: str                                     ''
    def parse_post_response(self, response):
        data = json.loads(response.text)
        for product in data['products']:
            item = ProductItem()
            attributes = AttributesItem()
            price = PriceItem()
            nutritional_information = NutritionalInformationItem()
            product_description = ProductDescriptionItem()

            for field in ['sku', 'brand', 'gtin13']:
                item[field] = product.get(field, None)
            yield item

            for field in ['attributes']:
                attributes[field] = product.get(field, None)
            yield attributes

            for field in ['price']:
                price[field] = product.get(field, None)
            yield price

            for field in ['nutritionalInformation']:
                nutritional_information[field] = product.get(field, None)
            yield nutritional_information

            for field in ['description', 'longDescription']:
                product_description[field] = product.get(field, None)
            yield product_description

        if data['nbPages'] > 1 and data['page'] < data['nbPages']:
            next_page = data['page'] + 1
            yield self.create_post_request(response.meta['category_path'], page=next_page)

    
    ## HELPER METHODS
    # Generar paths de categorias con sus subcategorias en todos los 3 niveles
    def generate_category_paths(self, category):
        paths = []
        for subcategory in category['categoriesLevel2']:
            for sub_subcategory in subcategory['categoriesLevel3']:
                path = f"{category['label']}/{subcategory['label']}/{sub_subcategory['label']}"
                paths.append(path)
        return paths