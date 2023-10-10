from .items.lider_items import ProductItem as LiderProductItem
from .items.jumbo_items import ProductItem as JumboProductItem

from products.models import Product, Price, Provider
from django.contrib.postgres.search import TrigramSimilarity

from asgiref.sync import sync_to_async

SIMILARITY_THRESHOLD = 0.7

class ProductPipeline:
    @sync_to_async
    def _lider_save_item(self, item, provider, product: None):
        if not product:
            product = Product(
                name=item['displayName'],
                brand=item['brand'],
                gtin13=item['gtin13']
            )
            product.save()
        
        product_price = Price(
            provider = provider,
            product = product,
            price = item['price']['BasePriceReference'],
            extra_data_price = item['price']
        )
        product_price.save()

    @sync_to_async
    def _jumbo_save_item(self, item, provider, product: None):
        if not product:
            product = Product(
                name=item['name'],
                brand=item['brand'],
                gtin13=item['items'][0]['ean']
            )
            product.save()
        
        # [0].items[0].ean Ean es el GTIN13 que está en el lider.
        # TODO: Tener ojo que pueden ser más de un item, por lo que hay que iterar
        # Por modos de prueba, se dejará para después el analisis
        product_price = Price(
            provider = provider,
            product = product,
            price = item['items'][0]['commertialOffer']['Price'],
            extra_data_price = item['items'][0]
        )
        product_price.save()

    async def process_item(self, item, spider):
        provider = await sync_to_async(Provider.objects.filter, thread_sensitive=True)(name=item['provider'])
        exists = await sync_to_async(provider.exists, thread_sensitive=True)()

        if not exists:
            provider = Provider(name=item['provider'])
            await sync_to_async(provider.save, thread_sensitive=True)()

        # TODO: en caso de que no se pueda obtener el GTIN13, se debe buscar por nombre
        # products = Product.objects.annotate(
        #     similarity=TrigramSimilarity('name', item['name'])
        #     ).filter(
        #         brand=item['brand'],
        #         similarity__gt=SIMILARITY_THRESHOLD
        #     ).order_by('-similarity')

        # create_product = True
        # if products.count() > 0:
        #     create_product = False
        #     product = products.first()
        #     print(f"El producto {item['name']} ya existe")
            
        # if products.count() > 1:
        #     print(f"El producto {item['name']} está duplicado")

        if isinstance(item, LiderProductItem):
            product = Product.objects.filter(gtin13=item['gtin13'])
            await self._lider_save_item(item, provider, product)
        if isinstance(item, JumboProductItem):
            product = Product.objects.filter(gtin13=item['items'][0]['ean'])
            await self._jumbo_save_item(item, provider, product)
        return item