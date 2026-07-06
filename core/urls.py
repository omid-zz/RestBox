from django.urls import path
from .views import Registerview, Loginview, Villaview, Reservationview

urlpatterns = [
    path('auth/register/', Registerview.as_view(), name = 'register'),
    path('auth/login/', Loginview.as_view(), name = 'login'),
    path('auth/villas/', Villaview.as_view(), name='villa'),
    path('auth/reservations/', Reservationview.as_view(), name='reserve')
]