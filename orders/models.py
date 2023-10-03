from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

from products.models import Product
from orders.cart import Cart


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    is_paid = models.BooleanField(default=False)
    discount = models.IntegerField(blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    zarinpal_authority = models.CharField(max_length=255, blank=True)
    zarinpal_ref_id = models.CharField(max_length=150, blank=True)
    zarinpal_data = models.TextField(blank=True)

    class Meta:
        ordering = ('is_paid', '-updated')

    def str(self):
        return f'{self.id}-{self.user}-{self.is_paid}-{self.updated}'

    def get_total_price(self):
        total = sum([item.get_cost() for item in self.items.all()])
        if self.discount:
            discount_price = Decimal(self.discount / 100) * total
            return round(total - discount_price, 2)
        return total

    def return_products_to_cart(self, request):
        cart = Cart(request)
        rec_cart = None
        for item in self.items.all():
            rec_cart = cart.add(item.product, item.quantity)
        return rec_cart


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)

    def str(self):
        return f'{self.order.id}-{self.product}-{self.price}-{self.quantity}'

    def get_cost(self):
        return self.price * self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(90)])
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code


