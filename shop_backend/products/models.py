from django.db import models


# Create your models here.
class Category(models.Model):
    naming = models.CharField(max_length=31)
    description = models.TextField(max_length=255)

    def __str__(self):
        return self.naming

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    """Represents position with its attributes"""
    naming = models.CharField(max_length=127)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    look = models.ImageField(upload_to='products/', blank=True)  # More confident with photo
    published_at = models.DateTimeField('Дата размещения', auto_now=True)
    description = models.TextField(max_length=127)

    def __str__(self):
        return self.naming

    # seller_link
    # commentaries
    # stars
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Seller(models.Model):
    # commentaries and mark
    # time_spent_in_trade
    # user_id
    # location
    ...
