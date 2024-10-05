from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='images/users/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reset_token = models.CharField(max_length=100, null=True, blank=True)

class Add_To_Cart(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    qty = models.IntegerField()
    img = models.ImageField(upload_to='images/customer/')
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, default= 1)