from django.contrib import messages
from products.models import Product

CART_SESSION_ID = 'cart'


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)

        if not cart:
            cart = self.session[CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['total_price'] = float(item['price']) * item['quantity']
            yield item

    def __len__(self):
        return len([key for key in self.cart.keys()])

    def add(self, product, quantity, replace_current_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if replace_current_quantity:
            self.cart[product_id]['quantity'] = min(quantity, 10)
            if quantity > 10:
                messages.error(self.request, 'You cannot add more than ten products', 'danger')
        else:
            if self.cart[product_id]['quantity'] + quantity <= 10:
                self.cart[product_id]['quantity'] += quantity
            else:
                messages.error(self.request, 'You cannot add more than ten products', 'danger')
        self.save()

    def remove(self, product):
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def get_total_price(self):
        return sum([float(item['price']) * item['quantity'] for item in self.cart.values()])

    def clear(self):
        del self.session[CART_SESSION_ID]
        self.save()
