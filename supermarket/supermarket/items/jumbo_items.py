# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    gtin13 = scrapy.Field() 
    brand = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    provider = scrapy.Field()