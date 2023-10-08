# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    sku = scrapy.Field()
    gtin13 = scrapy.Field()
    brand = scrapy.Field()

class AttributesItem(scrapy.Item):
    attributes = scrapy.Field()

class PriceItem(scrapy.Item):
    price = scrapy.Field()

class NutritionalInformationItem(scrapy.Item):
    nutritionalInformation = scrapy.Field()

class ProductDescriptionItem(scrapy.Item):
    description = scrapy.Field()
    longDescription = scrapy.Field()