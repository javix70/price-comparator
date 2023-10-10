import scrapy

class ProductItem(scrapy.Item):
    gtin13 = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    displayName = scrapy.Field()
    provider = scrapy.Field()
