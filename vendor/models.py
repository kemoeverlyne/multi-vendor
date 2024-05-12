from django.db import models
from userauths.models import User, Profile
from django.utils.text import slugify

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='vendor/', null=True, blank=True, default="vendor/default.jpg")
    name = models.CharField(max_length=100, help_text='Vendor name', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    mobile = models.CharField(max_length=100, help_text='Mobile Number', null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=500, unique=True, null=True, blank=True)


    def __str__(self):
        return self.name if self.name else ""


    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['-date'] 

    def save(self, *args, **kwargs):
        if self.slug == None or self.slug =='': 
            self.slug = slugify(self.name)
        super(Vendor, self).save(*args, **kwargs)