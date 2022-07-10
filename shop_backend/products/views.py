from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics

from products.models import Product
from products.serializers import ProductSerializer
from rest_framework.permissions import BasePermission, SAFE_METHODS

from products.models import Category
from products.serializers import CategorySerializer


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ProductViewSet(viewsets.ModelViewSet):  # or readonly parent
    permission_classes = [ReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoriesListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        cat_id = self.request.query_params.get('cat_id')
        return Product.objects.filter(category__id=cat_id)
