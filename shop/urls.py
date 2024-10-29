from django.urls import path
from django.utils.regex_helper import normalize
from . import views
from .views import test_recommendation_view  # Importez la nouvelle vue

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:category_slug>/', views.shop, name='categries'),
    path('shop/<slug:category_slug>/<slug:product_details_slug>/', views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('review/<int:product_id>/', views.review, name='review'),
    path('test-recommend/', test_recommendation_view, name='test_recommend')
]
