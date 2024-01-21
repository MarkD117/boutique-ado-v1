from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    # Specify that the product ID should be an integer as otherwise
    # navigating to products/add will interpret the string add as
    # a product id. Which will cause that view to throw an error.
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
]
