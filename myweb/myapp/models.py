from django.db import models
from datetime import datetime 

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='images/users/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reset_token = models.CharField(max_length=100, null=True, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=datetime.now)

class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.TextField()
    price = models.FloatField()
    qty = models.IntegerField()
    status = models.TextField()    
    img = models.ImageField(upload_to='images/products/')
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default= 1)