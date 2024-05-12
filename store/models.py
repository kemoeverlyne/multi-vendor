from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save

from vendor.models import Vendor
from userauths.models import User, Profile




class Category(models.Model):
    title = models.CharField(max_length=100, help_text='Category title', null=True, blank=True)
    image = models.FileField(upload_to='category/', null=True, blank=True, default="category/default.jpg")
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=100, help_text='Category title', null=True, blank=True)
    image = models.FileField(upload_to='products/', null=True, blank=True, default="image/product.jpg")
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    stock_qty = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)

    STATUS = (
        ('draft', 'Draft'),
        ('disabled', 'Disabled'),
        ('in_review', 'In Review'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=100, choices=STATUS, default='draft')

    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=0, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    pid = ShortUUIDField(unique=True, length=10, prefix="P", alphabet="abcdefg123456789", null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.slug == None or self.slug =='': 
            self.slug = slugify(self.title)
            super(Product, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        self.rating = self.product_rating()
        super(Product, self).save(update_fields=['rating'])

    def orders(self):
        return CartOrderItem.objects.filter(product=self).count()

    def gallery(self):
        return Gallery.objects.filter(product=self)
    
    def specification(self):
        return Specification.objects.filter(product=self)
    
    def size(self):
        return Size.objects.filter(product=self)
    
    def color(self):
        return Color.objects.filter(product=self)
    
    def product_rating(self):
        product_rating = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg('rating'))
        return product_rating['avg_rating']
    
    def rating_count(self):
        return Review.objects.filter(product=self).count()
    

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-date']

    def __str__(self):
        return self.title
    




class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.FileField(upload_to='gallery/', default='gallery.jpg', null=True, blank=True)
    active = models.BooleanField(default=True)
    gid = ShortUUIDField(unique=True, length=10, prefix="G", alphabet="abcdefg123456789")

    def __str__(self):
        return self.product.title
    
    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, help_text='Enter the specification title', null=True, blank=True)
    content = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.title
    

class Size(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000, help_text='Enter the product size name', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)

    def __str__(self):
        return self.name
    

class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000, help_text='Enter the color name', null=True, blank=True)
    color_code = models.CharField(max_length=100, help_text='Enter the HEX color code', null=True, blank=True)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    tax_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    country = models.CharField(max_length=100, help_text='Country', null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cart_id}"


class CartOrder(models.Model):
    vendor = models.ManyToManyField(Vendor, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    tax_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    PAYMENT_STATUS = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('cancelled', 'Cancelled'),
    )
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default='pending')
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Fullfilled', 'Fullfilled'),
        ('Cancelled', 'Cancelled'),
    )
    order_status = models.CharField(choices=ORDER_STATUS, max_length=100, default='pending')

    #Coupon
    initial_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    saved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)

    #Bio Data
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)

    #Shipping Address
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    #Stripe, Coupon
    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    oid = ShortUUIDField(unique=True, length=10, prefix="O", alphabet="abcdefg123456789")
    date = models.DateTimeField(auto_now_add=True)

    def update_totals(self, shipping_amount, tax_fee, service_fee, sub_total, initial_total, total):
        """
        Update the order totals.
        """
        self.shipping_amount = shipping_amount
        self.tax_fee = tax_fee
        self.service_fee = service_fee
        self.sub_total = sub_total
        self.initial_total = initial_total
        self.total = total
        self.save()
        
    def __str__(self):
        return f"{self.oid} - {self.full_name}"
    
    # def get_order_items(self):
    #     return CartOrderItem.objects.filter(order=self)
    

class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    tax_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    country = models.CharField(max_length=100, help_text='Country', null=True, blank=True)

    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)

    #Coupon
    coupon = models.ManyToManyField("store.Coupon", blank=True)
    initial_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    saved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)

    oid = ShortUUIDField(unique=True, length=10, prefix="O", alphabet="abcdefg123456789")
    date = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"{self.oid}"
    


class ProductFaq(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    email = models.EmailField(max_length=100, null=True, blank=True)
    question = models.CharField(max_length=1000)
    answer = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name_plural = 'Product FAQs'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    review = models.TextField(max_length=1000)
    reply = models.TextField(max_length=1000)

    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    rating = models.IntegerField(default=None, choices=RATING_CHOICES)
    
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title
    
    class Meta:
        verbose_name_plural = 'Reviews'

    def profile(self):
        return Profile.objects.get(user=self.user)
    

@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, created, **kwargs):
    if instance.product:
        instance.product.save()

    #if created:
    #    product = instance.product
    #    reviews = Review.objects.filter(product=product)
    #    total = 0
    #    for review in reviews:
    #        total += review.rating
    #    product.rating = total / reviews.count()
    #    product.save()


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist - {self.product.title} - {self.user.username} -  {self.date}"
    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(CartOrder, on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.order:
            return self.order.oid
        else:
            return f"Notification - {self.pk}"
        

class Coupon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    used_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=1000)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coupon - {self.code} - {self.discount}% - {self.vendor}"


class Tax(models.Model):
    country = models.CharField(max_length=100)
    rate = models.IntegerField(default=5, help_text='Numbers added here are in percentage e.g 5%')
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.country} - {self.rate}%"
    
    class Meta:
        verbose_name_plural = 'Taxes'
        ordering = ['country']
        