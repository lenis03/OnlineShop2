from django.urls import path, include

from products import views

app_name = 'products'

bucket_urls = [
    path('', views.ProductBucketView.as_view(), name='product_bucket'),
    path('delete_obj/<str:key>', views.DeleteObjectBucketView.as_view(), name='delete_obj'),
    path('download_obj/<str:obj_name>', views.DownloadBucketObjectView.as_view(), name='download_obj'),
]

urlpatterns = [
    path('', views.ProductsListView.as_view(), name='product_list'),
    path('bucket/', include(bucket_urls)),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
