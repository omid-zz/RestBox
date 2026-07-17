from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Villa, Availability, Reservation, Payment

# Register your models here.
User = get_user_model()
admin.site.register(User)
admin.site.register(Villa)
admin.site.register(Availability)
admin.site.register(Reservation)
admin.site.register(Payment)