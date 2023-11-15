from .items.lider_items import ProductItem as LiderProductItem
from .items.jumbo_items import ProductItem as JumboProductItem

from products.models import Product, Price, Provider

from asgiref.sync import sync_to_async

SIMILARITY_THRESHOLD = 0.7

class ProductPipeline:
    def __init__(self):
        self.product_cache = {}
        self.provider_cache = {}
        self.provider_price_cache = { }
        self.price_key = { LiderProductItem: 'BasePriceReference', JumboProductItem: 'Price'}

    @sync_to_async
    def _save_item(self, item, provider, product: None, key):
        if not product:
            product = Product(
                name=item['name'],
                brand=item['brand'],
                gtin13=item['gtin13']
            )
            product.save()
        
        product_price = Price(
            price=item['price'][self.price_key[item.__class__]],
            provider=provider,
            product=product,
            extra_data_price=item['price']
        )

        self.provider_price_cache[key] = product_price
        product_price.save()

    async def process_item(self, item, spider):
        provider = await self.get_or_create_provider(item['provider'])
        product = await self.get_or_load_product(item)

        if product:
            key = f"{product.gtin13}-{provider.name}"
            if key in self.provider_price_cache.keys():
                return

        await self._save_item(item, provider, product, key)

    async def get_or_create_provider(self, key):
        if key in self.provider_cache.keys():
            return self.provider_cache[key]

        provider, _ = await Provider.objects.aget_or_create(name=key)
        self.provider_cache[key] = provider
        return provider

    async def get_or_load_product(self, item):
        if item['gtin13'] in self.product_cache.keys():
            return self.product_cache[item['gtin13']] 

        product = await Product.objects.filter(gtin13=item['gtin13']).afirst()
        
        self.product_cache[item['gtin13']] = product
        return product