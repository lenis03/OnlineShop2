from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from products.models import Product
from orders.forms import AddToCartForm
from orders.cart import Cart
from orders.models import Order, OrderItems


class CartView(View):
    template_name = 'orders/cart.html'

    def get(self, request):
        cart = Cart(request)
        return render(request, self.template_name, {'cart': cart})


class CartAddView(View):
    form_class = AddToCartForm

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = self.form_class(request.POST)

        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])

        return redirect('orders:cart')


class CartItemRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderDetailView(LoginRequiredMixin, View):
    template_name = 'orders/order_detail.html'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, self.template_name, {'order': order})


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user)

        for item in cart:
            OrderItems.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
        cart.clear()
        return redirect('orders:order_detail', order.id)
