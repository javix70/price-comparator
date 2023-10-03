from django.db import models
from .product import Product
from .provider import Provider

class ProviderProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    details = models.JSONField()

    def __str__(self):
        return f"Details for {self.product} from {self.provider}"