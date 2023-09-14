from django.urls import path

from products import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductsListView.as_view(), name='product_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
