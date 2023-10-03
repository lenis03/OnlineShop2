from django.contrib import admin

from orders.models import Order, OrderItems, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItems
    raw_id_fields = ('product', )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'updated', 'is_paid']
    list_filter = ('is_paid', )
    inlines = (OrderItemInline, )


admin.site.register(Coupon)
