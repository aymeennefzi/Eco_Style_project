from django.urls import path
from . import views

app_name = 'recycle'

urlpatterns = [
    path('', views.recycle, name='recycle'),
    path('my-items/', views.my_recycled_items, name='my_recycled_items'),
    path('donate/', views.donate_item, name='donate_item'),
    path('drop-points/', views.drop_points_list, name='drop_points_list'),
    path('item/<int:item_id>/', views.recycled_item_detail, name='recycled_item_details'),
    path('drop-point/<int:point_id>/', views.drop_point_detail, name='drop_point_details'),
   # path('search/', views.search, name='search'),
]