from django.shortcuts import render
from django.views import View


class CartView(View):
    template_name = 'orders/cart.html'
    def get(self, request):
        return render(request, self.template_name, )
