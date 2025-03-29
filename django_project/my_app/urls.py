from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stock/<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('stock/<str:symbol>/add-favorite/', views.add_to_favorites, name='add_to_favorites'),
    path('stock/<str:symbol>/remove-favorite/', views.remove_from_favorites, name='remove_from_favorites'),
    path('search/', views.search_stocks, name='search_stocks'),
]