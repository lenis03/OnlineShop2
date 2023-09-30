from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from products.models import Product
from orders.forms import AddToCartForm
from orders.cart import Cart


class CartView(View):
    template_name = 'orders/cart.html'

    def get(self, request):
        return render(request, self.template_name, )


class CartAddView(View):
    form_class = AddToCartForm

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = self.form_class(request.POST)

        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])

        return redirect('orders:cart')



