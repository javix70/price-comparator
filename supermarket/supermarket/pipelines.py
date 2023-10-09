# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from .items.lider_items import ProductItem as LiderProductItem
from .items.jumbo_items import ProductItem as JumboProductItem
from products.models import *
from asgiref.sync import sync_to_async

class ProductPipeline:
    @sync_to_async
    def _lider_save_item(self, item):
        product = Product(
            gtin13=item['gtin13'],
            brand=item['brand'],
        )
        product.save()

    @sync_to_async
    def _jumbo_save_item(self, item):
        product = Product(
            gtin13=item['sku'],
            brand=item['brand'],
        )
        product.save()

    async def process_item(self, item, spider):
        if isinstance(item, LiderProductItem):
            await self._lider_save_item(item)
        if isinstance(item, JumboProductItem):
            await self._jumbo_save_item(item)
        return item