from rest_framework import serializers

from products.models import Product

from products.models import Category


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'naming', 'category', 'price'
                  , 'look', 'published_at', 'description',)
        model = Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'naming', 'description',)
