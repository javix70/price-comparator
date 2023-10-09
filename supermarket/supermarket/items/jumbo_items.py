# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    sku = scrapy.Field()
    brand = scrapy.Field()
    name = scrapy.Field()
    items = scrapy.Field()