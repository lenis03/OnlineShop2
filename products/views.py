from django.shortcuts import render, get_object_or_404
from django.views import View

from products.models import Product


class ProductsListView(View):
    def get(self, request):
        products = Product.objects.filter(available=True)
        return render(request, 'products/products_list.html', {'products': products})


class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        return render(request, 'products/product_detail.html', {'product': product})