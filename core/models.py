from django.contrib.auth.models import AbstractUser
from django.db import models

class User(models.Model):
    roles = [('host', 'host'),('guest', 'guest')]
    full_name = models.CharField(max_length= 80)
    email = models.EmailField(unique= True)
    role = models.CharField(max_length= 8, choices= roles)
    create_time = models.DateTimeField(auto_now_add= True)
    username_field = 'email'
    required_fields = ['username', 'full_name', 'role']
    def __str__(self):
        return f'{self.full_name} {self.role}'