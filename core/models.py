from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    roles = [('host', 'host'),('guest', 'guest')]
    full_name = models.CharField(max_length= 80)
    email = models.EmailField(unique= True)
    role = models.CharField(max_length= 8, choices= roles)
    create_time = models.DateTimeField(auto_now_add= True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'role']
    def __str__(self):
        return f'{self.full_name} {self.role}'

class Villa(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(max_length=100)
    price_per_night = models.IntegerField()
    capacity = models.PositiveIntegerField()
    amenities = models.JSONField()

class Availability(models.Model):
    villa_id = models.ForeignKey(Villa, on_delete=models.CASCADE)
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('villa_id', 'date')

class Reservation(models.Model):
    guest_id = models.ForeignKey(User, on_delete=models.CASCADE)
    villa_id = models.ForeignKey(Villa, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.IntegerField()
    status_choices = [
        ('pending_payment', 'pending'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
        ('completed', 'completed')
    ]
    status = models.CharField(max_length=100, choices=status_choices, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)