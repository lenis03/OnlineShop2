from django.db import models
from django.contrib.auth import get_user_model

from products.models import Product


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='orders')
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('is_paid', '-updated')

    def str(self):
        return f'{self.id}-{self.user}-{self.is_paid}-{self.updated}'

    def get_total_price(self):
        return sum([item.get_cost() for item in self.items.all()])


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=1)

    def str(self):
        return f'{self.order.id}-{self.product}-{self.price}-{self.quantity}'

    def get_cost(self):
        return self.price * self.quantity
