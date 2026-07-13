from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Villa, Availability, Reservation

# Register your models here.
# دریافت مدل کاربر اختصاصی شما (چون با ایمیل لاگین کردی)
User = get_user_model()
# 🌟 معرفی مدل‌ها به پنل ادمین جنگو
admin.site.register(User)
admin.site.register(Villa)
admin.site.register(Availability)
admin.site.register(Reservation)