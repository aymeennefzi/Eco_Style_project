from django.urls import path
from django.utils.regex_helper import normalize
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:category_slug>/', views.shop, name='categries'),
    path('shop/<slug:category_slug>/<slug:product_details_slug>/', views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('review/<int:product_id>/', views.review, name='review'),



    #AZIZ
    
    #WISHLIST
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),


    #NOTIFACTIONS
    path('notifications/', views.list_notifications, name='list_notifications'),
    path('notifications/<int:notification_id>/', views.get_notification, name='get_notification'),
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/<int:notification_id>/update/', views.update_notification, name='update_notification'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/check/<int:user_id>/<int:product_id>/', views.check_notification, name='check_notification'),  
    #path('churn-prediction/', views.churn_prediction_view, name='churn_prediction'),
]
