from django.contrib import admin
from .models import Category, Product, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, ProductFaq, Review, Wishlist, Notification, Coupon, Tax


# Inline classes for the admin panel
class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1
class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1

class SizeInline(admin.TabularInline):
    model = Size
    extra = 1

class ColorInline(admin.TabularInline):
    model = Color
    extra = 1


# Admin classes for the models
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'stock_qty', 'in_stock', 'shipping_amount', 'vendor', 'featured']
    list_editable = ['featured']
    list_filter = ['date']
    search_fields = ['title']
    inlines = [GalleryInline, SpecificationInline, SizeInline, ColorInline]

    
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'qty', 'price', 'total']
    search_fields = ['user__username', 'product__title']

class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['payment_status', 'order_status']
    list_display = ['oid', 'buyer','email', 'total', 'payment_status', 'order_status', 'date']
    search_fields = ['buyer__username', 'oid']

class CartOrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'qty', 'price']
    search_fields = ['order__oid', 'product__title']

class ProductFaqAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'question', 'active']
    search_fields = ['user__username', 'product__title', 'question']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'active']
    search_fields = ['user__username', 'product__title']

class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product']
    search_fields = ['user__username', 'product__title']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'vendor', 'seen']
    search_fields = ['user__username', 'vendor__name']

class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'vendor', 'discount', 'active']
    search_fields = ['code', 'vendor__name']


# Register the models to the admin panel
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItem)
admin.site.register(ProductFaq, ProductFaqAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Tax)

