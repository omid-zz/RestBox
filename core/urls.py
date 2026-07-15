from django.urls import path
from .views import Registerview, Loginview, Villaview, Villadetailview, Reservationview, Reservationcreateview, Paymentverifyview

urlpatterns = [
    path('auth/register/', Registerview.as_view(), name = 'register'),
    path('auth/login/', Loginview.as_view(), name = 'login'),
    path('villas/', Villaview.as_view(), name='villas'),
    path('villas/<int:villa_id>/', Villadetailview.as_view(), name='villa_detail'),
    path('reservations/', Reservationview.as_view(), name='reservations'),
    path('reservation/', Reservationcreateview.as_view(), name = 'reservation-create'),
    path('payment/verify/', Paymentverifyview.as_view(), name='payments')
]