from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate
from .serializers import Userregisterserializer
from .models import Villa, Availability, Reservation
from .serializers import Villaserializer, Availabilityserializer, Reservationserializer
from datetime import timedelta

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
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def get(self, request):
        query_set = Villa.objects.all()
        city = request.query_params.get('city')
        if city:
            query_set = query_set.filter(city__icontains=city)

        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        if check_in and check_out:
            check_in = parse_date(check_in)
            check_out = parse_date(check_in)

            if check_in and check_out and check_in < check_out:
                total_days = (check_out - check_in).days
                requested_dates = [check_in + timedelta(days=i) for i in range(total_days)]

                validvillas_id = []
                for villa in query_set:
                    days_count = Availability.objects.filter(villa_id=villa, date__in=requested_dates, is_available=True).count()
                    if days_count == total_days:
                        validvillas_id.append(villa.id)

                query_set = query_set.filter(id__in=validvillas_id)
            
        serializer = Villaserializer(query_set, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != 'host':
            return Response({"error": "Only host can create villa"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = Villaserializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Villadetailview(APIView):
    def get(self, request, id):
        villa = Villa.objects.get(pk=id)
        if villa:
            serializer = Villaserializer(villa)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

class Reservationview(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def post(self, request):
        if request.user.role != 'guest':
            return Response({"error": "Only guest can reserve villa"}, status=status.HTTP_403_FORBIDDEN)

        serializer = Reservationserializer(data=request.data)
        if serializer.is_valid():
            villa = serializer.validated_data['villa_id']
            check_in = serializer.validated_data['check_in']
            check_out = serializer.validated_data['check_out']
        
            concurency = Reservation.objects.filter(villa_id=villa, check_in__lt=check_out, check_out__gt=check_in)
            if concurency.exists():
                return Response({"error": "This villa has been reserved and is not valid for the given date"}, status=status.HTTP_400_BAD_REQUEST)

            total_days = (check_out - check_in).days
            dates = [check_in + timedelta(days=i) for i in range(total_days)]
            availabilities = Availability.objects.filter(villa_id=villa, date__in=dates, is_available=True)
            if availabilities.count() != total_days:
                return Response({"error": "Villa is not available in some dates you chose"}, status=status.HTTP_400_BAD_REQUEST)

            total_price = sum(d.villa_id.price_per_night for d in availabilities)
            reservation = serializer.save(guest_id=request.user, total_price=total_price)
            availabilities.update(is_available=False)
            return Response({"message": "Villa reserved successfully", "reservation": Reservationserializer(reservation).data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)