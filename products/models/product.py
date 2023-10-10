from django.contrib.postgres.indexes import GinIndex

from django.db import models

class Product(models.Model):
    brand = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    gtin13 = models.CharField(max_length=13, null=True, blank=True)

    def __str__(self):
        return f"{self.brand}: {self.name}"

    class Meta:
            indexes = [
                GinIndex(fields=['name'], name='idx_name_gin_trgm', opclasses=['gin_trgm_ops']),
            ]