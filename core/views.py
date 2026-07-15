from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate
from .models import Villa, Availability, Reservation, Payment
from .serializers import Userregisterserializer, Villaserializer, Availabilityserializer, Reservationserializer
from datetime import timedelta, datetime
from django.db import transaction

class Registerview(APIView):
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email = email, password = password)
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
            check_out = parse_date(check_out)

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
    
class Reservationcreateview(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        if request.user.role != 'guest':
            return Response({"error": "only guests can reserve villa"}, status=status.HTTP_403_FORBIDDEN)
        villa_id = request.data.get('villa_id')
        check_instr = request.data.get('check_in')
        check_outstr = request.data.get('check_out')
        if not all([villa_id, check_instr, check_outstr]):
            return Response({"error: villa_id, check_instr and check_outstr needed"},status= status.HTTP_400_BAD_REQUEST)
        try:
            check_in = datetime.strptime(check_instr, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_outstr, "%Y-%m-%d").date()
            villa = Villa.objects.get(pk= villa_id)
        except(ValueError, Villa.DoesNotExist):
            return Response({"error: invalid date format or not found"}, status= status.HTTP_400_BAD_REQUEST)
        if check_in >= check_out:
            return Response({"error: check-in must be before check-out"}, status= status.HTTP_400_BAD_REQUEST)
        requested_dates = []
        current_date = check_in
        while(current_date < check_out):
            requested_dates.append(current_date)
            current_date += timedelta(days=1)
        nights = len(requested_dates)
        try:
            with transaction.atomic():
                calender_rows = Availability.objects.select_for_update().filter(villa_id = villa, date__in = requested_dates)
                available_days = calender_rows.filter(is_available=True).count()
                if available_days != nights:
                    return Response({"error: villa not available in the chosen dates"}, status= status.HTTP_400_BAD_REQUEST)
                price_total = nights * villa.price_per_night
                reservation = Reservation.objects.create(
                    guest_id = request.user,
                    villa_id = villa,
                    check_in = check_in,
                    check_out = check_out,
                    total_price = price_total,
                    status = 'pending'
                )
                calender_rows.update(is_available = False)
                payment_url = f"https://gateway.example.com/pay/abc{reservation.id}"
                response_data = {
                    'reservation_id': reservation.id,
                    'status': reservation.status,
                    'total_price': reservation.total_price,
                    'payment_url': payment_url
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({f"error: {e}"}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)

class Paymentverifyview(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []
    
    def post(self, request):
        reservation_id = request.data.get('reservation_id')
        payment_status = request.data.get('status')
        gateway_ref = request.data.get('gateway_ref')
        if not (reservation_id and payment_status):
            return Response({"error": "reservation_id and status can't be empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                reservation = Reservation.objects.select_for_update().get(pk=reservation_id)
                if reservation.status != 'pending':
                    return Response({"error": f"invalid state. reservation is in {reservation.status} status"}, status=status.HTTP_400_BAD_REQUEST)
                
                payment = Payment.objects.create(
                    reservation_id=reservation,
                    amount=reservation.total_price,
                    status='success' if payment_status == 'success' else 'failed',
                    gateway_ref=gateway_ref
                )
                if payment_status == "success":
                    reservation.status = "confirmed"
                    reservation.save()
                    return Response({
                        "message": "payment was successful. reservation confirmed",
                        "reservation_id": reservation_id,
                        "status": reservation.status,
                        "gateway_ref": payment.gateway_ref},
                        status=status.HTTP_200_OK)
                else:
                    reservation.status = "failed"
                    reservation.save()
                    days = (reservation.check_out - reservation.check_in).days
                    dates = [reservation.check_in + timedelta(days=i) for i in range(days)]
                    Availability.objects.filter(
                        villa_id=reservation.villa_id,
                        date__in=dates
                    ).update(is_available=True)
                    return Response({
                        "message": "payment failed",
                        "reservation_id": reservation_id,
                        "status": reservation.status},
                        status=status.HTTP_200_OK)

        except Reservation.DoesNotExist:
            return Response({"error": "reservation does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"some exception happend: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)