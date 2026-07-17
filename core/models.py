from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [('host', 'host'),('guest', 'guest')]
    full_name = models.CharField(max_length= 80)
    email = models.EmailField(unique= True)
    role = models.CharField(max_length= 8, choices= ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add= True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'role']
    def __str__(self):
        return f'{self.full_name} {self.role}'

class Villa(models.Model):
    villa_id = models.AutoField(primary_key=True)
    host_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    price_per_night = models.IntegerField()
    capacity = models.PositiveIntegerField()
    amenities = models.JSONField()

class Availability(models.Model):
    availability_id = models.AutoField(primary_key=True)
    villa_id = models.ForeignKey(Villa, on_delete=models.CASCADE)
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('villa_id', 'date')

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'pending_payment'),
        ('confirmed', 'confirmed'),
        ('failed', 'failed'),
        ('cancelled', 'cancelled'),
    ]
    reservation_id = models.AutoField(primary_key=True)
    guest_id = models.ForeignKey(User, on_delete=models.CASCADE)
    villa_id = models.ForeignKey(Villa, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.IntegerField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.IntegerField()
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('success', 'success'),
        ('failed', 'failed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    gateway_ref = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)