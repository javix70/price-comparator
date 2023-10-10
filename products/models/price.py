from django.db import models
from .provider import Provider
from .product import Product

class Price(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="prices")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")

    price = models.DecimalField(max_digits=10, decimal_places=0)
    extra_data_price = models.JSONField(default=dict)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.price} from {self.provider}"