from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages

from products.models import Product
from products import tasks
from utils import IsAdminUser


class ProductsListView(View):
    def get(self, request):
        products = Product.objects.filter(available=True)
        return render(request, 'products/products_list.html', {'products': products})


class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        return render(request, 'products/product_detail.html', {'product': product})


class ProductBucketView(IsAdminUser, View):
    template_name = 'products/product_bucket.html'

    def get(self, request):
        objects = tasks.get_product_bucket_objects_task()
        return render(request, self.template_name, {'objects': objects})


class DeleteObjectBucketView(IsAdminUser, View):
    def get(self, request, key):
        tasks.delete_obj_bucket_task.delay(key)
        messages.info(request, 'Your object will be delete soon!', 'info')
        return redirect('products:product_bucket')


class DownloadBucketObjectView(IsAdminUser, View):
    def get(self, request, obj_name):
        tasks.download_obj_from_bucket.delay(obj_name)
        messages.info(request, 'Your download will start soon.', 'info')
        return redirect('products:product_bucket')
