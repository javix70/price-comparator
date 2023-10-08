# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from .items.lider_items import *
from products.models import *
import asyncio
from asgiref.sync import sync_to_async

class ProductPipeline:
    @sync_to_async
    def _save_item(self, item):
        product = Product(
            gtin13=item['gtin13'],
            brand=item['brand'],
        )
        product.save()

    async def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            await self._save_item(item)
        return item