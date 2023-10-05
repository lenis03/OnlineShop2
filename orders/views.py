from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
from django.conf import settings
import json
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime

from products.models import Product
from orders.forms import AddToCartForm, CouponApplyForm
from orders.cart import Cart
from orders.models import Order, OrderItems, Coupon


class CartView(View):
    template_name = 'orders/cart.html'
    form_class = AddToCartForm

    def get(self, request):
        cart = Cart(request)
        form = self.form_class
        return render(request, self.template_name, {'cart': cart, 'form': form})


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
    form_class = CouponApplyForm

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        form = self.form_class
        return render(request, self.template_name, {'order': order, 'form': form})


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


if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = "https://{sandbox}.zarinpal.com/pg/StartPay/{authority}"
CallbackURL = 'http://127.0.0.1:8000/orders/verify'


class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        request.session['order_pay'] = {
            'order_id': order.id,
        }

        req_data = {
            "MerchantID": settings.ZARINPALL_MERCHANT_ID,
            "Amount": int(order.get_total_price() * 50000),
            "Description": f'OrderID: {order.id}, User: {order.user.user_name}',
            "Phone": f'{request.user.phone_number}',
            "CallbackURL": request.build_absolute_uri(reverse('orders:order_verify')),
        }

        request_header = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        res = requests.post(ZP_API_REQUEST, data=json.dumps(req_data), headers=request_header)
        print(res)
        # print(res.json()['data'])

        data = res.json()
        print(data)
        authority = data['Authority']
        order.zarinpal_authority = authority
        order.save()

        if 'errors' not in data or len(data['errors']) == 0:
            return redirect(ZP_API_STARTPAY.format(sandbox=sandbox, authority=authority))
        else:
            print(data['errors'])
            order.return_products_to_cart(request)
            messages.error(request, 'Error from zarinpal', 'danger')
            return redirect('orders:cart')


class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        payment_authority = request.GET.get('Authority')
        payment_status = request.GET.get('Status')
        order = get_object_or_404(Order, zarinpal_authority=payment_authority)

        if payment_status == 'OK':
            request_header = {
                "accept": "application/json",
                "content-type": "application/json",
            }

            req_data = {
                'MerchantID': settings.ZARINPALL_MERCHANT_ID,
                'Amount': int(order.get_total_price() * 50000),
                'Authority': payment_authority,
            }

            res = requests.post(
                ZP_API_VERIFY,
                data=json.dumps(req_data),
                headers=request_header,

            )
            print(res.json())
            if 'errors' not in res.json():
                data = res.json()
                payment_code = data['Status']
                if payment_code == 100:
                    order.is_paid = True
                    order.zarinpal_ref_id = data['RefID']
                    order.zarinpal_data = data
                    order.save()
                    messages.error(request, 'Your payment has been successfully completed!', 'success')
                    return redirect('products:product_list')

                elif payment_code == 101:
                    messages.info(request, 'Your payment has been successfully completed.'
                                           ' Of course, this transaction has already been registered!', 'info')
                    return redirect('products:product_list')

                else:
                    order.return_products_to_cart(request)
                    error_code = res.json()['errors']['code']
                    error_message = res.json()['errors']['message']
                    messages.error(request, f'The transaction was unsuccessful! {error_message} {error_code} ', 'danger')
                    return redirect('orders:cart')

        else:
            order.return_products_to_cart(request)
            messages.error(request, 'The transaction was unsuccessful or canceled by user !', 'danger')
            return redirect('orders:cart')


class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponApplyForm

    def post(self, request, order_id):
        now = datetime.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code__exact=code, valid_from__lte = now, valid_to__gte=now, active=True)
            except Coupon.DoesNotExist:
                messages.error(request, 'This coupon does not exist', 'danger')
                return redirect('orders:order_detail', order_id)

            order = get_object_or_404(Order, id=order_id)
            order.discount = coupon.discount
            order.save()
            return redirect('orders:order_detail', order_id)


class ChangeProductQuantity(LoginRequiredMixin, View):
    form_class = AddToCartForm

    def post(self, request, product_id):
        form = self.form_class(request.POST)
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'], replace_current_quantity=True)
            return redirect('orders:cart')
        else:
            messages.error(self.request, 'You cannot add more than ten products', 'danger')
            return redirect('orders:cart')



