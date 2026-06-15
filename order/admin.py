from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    fields = ('model_3d', 'material', 'material_name', 'color', 'quantity', 'scale', 'price')

    readonly_fields = ('model_3d', 'material_name', 'color', 'quantity', 'scale', 'price')

    can_delete = False
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username')

    readonly_fields = ('user', 'total_price', 'created_at', 'updated_at')

    inlines = [OrderItemInline]

    fieldsets = (
        ('Основная информация о заказе', {
            'fields': ('user', 'total_price', 'created_at', 'updated_at')
        }),
        ('Управление заказом', {
            'fields': ('status',)
        }),
    )
