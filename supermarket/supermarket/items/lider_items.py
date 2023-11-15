import scrapy

class ProductItem(scrapy.Item):
    gtin13 = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    name = scrapy.Field()
    provider = scrapy.Field()
