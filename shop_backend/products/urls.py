from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from products.views import CategoriesListView
from products.views import ProductViewSet
from products.views import ProductsByCategoryView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register('products', ProductViewSet, basename='products')
urlpatterns = [
    path('', include(router.urls)),
    path('categories', CategoriesListView.as_view(), name="Categories"),
    path('prod_from_category', ProductsByCategoryView.as_view(), name='Category')
]
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
