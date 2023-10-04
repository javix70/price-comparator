from django.db import models

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=255)
    gtin13 = models.CharField(max_length=13)

    def __str__(self):
        return self.display_name
