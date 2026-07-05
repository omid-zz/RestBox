from django.urls import path
from .views import Registerview, Loginview

urlpatterns = [
    path('auth/register/', Registerview.as_view(), name = 'register'),
    path('auth/login/', Loginview.as_view(), name = 'login')
]