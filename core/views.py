from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import Userregisterserializer

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
