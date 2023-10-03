# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SupermarketItem(scrapy.Item):
    pass


class ProductItem(scrapy.Item):
    ID = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    gtin13 = scrapy.Field()