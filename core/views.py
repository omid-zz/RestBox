from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import Userregisterserializer
from .models import Villa, Reservation
from .serializers import Villaserializer, Reservationserializer
from datetime import datetime

class Registerview(APIView):
    def post(self, request):
        serializer = Userregisterserializer(data = request.data)
        if(serializer.is_valid()):
            user = serializer.save()
            token, created = Token.objects.get_or_create(user = user)
            return Response({"message": "User registered successfully.",
                             "token": token.key},
                            status = status.HTTP_201_CREATED)
        return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)

class Loginview(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username = email, password = password)
        if user:
            token, created = Token.objects.get_or_create(user = user)
            return Response({"token": token.key}, status= status.HTTP_200_OK)
        return Response({"error": "Invalid email or password."}, status= status.HTTP_400_BAD_REQUEST)

class Villaview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        villas = Villa.objects.all()
        serializer = Villaserializer(villas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        if request.user.role != 'host':
            return Response({"error": "Only host can create villa"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = Villaserializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Reservationview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'guest':
            return Response({"error": "Only guest can reserve villa"}, status=status.HTTP_403_FORBIDDEN)

        serializer = Reservationserializer(data=request.data)
        if serializer.is_valid():
            villa = serializer.validated_data['villa']
            check_in = serializer.validated_data['check_in']
            check_out = serializer.validated_data['check_out']
        
            concurency = Reservation.objects.filter(villa=villa, check_in__lt=check_out, check_out__gt=check_in)
            if concurency.exists():
                return Response({"error": "This villa has been reserved and is not valid for the given date"}, status=status.HTTP_400_BAD_REQUEST)
            total_price = (check_out - check_in).days * villa.price_per_night
            serializer.save(guest=request.user, total_price=total_price)
            return Response({"message": "Villa reserved successfully", "total_price": total_price})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)