from rest_framework import serializers
from .models import User, Villa, Availability, Reservation

class Userregisterserializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['email'],
            email = validated_data['email'],
            full_name = validated_data['full_name'],
            role = validated_data['role'],
            password = validated_data['password']
        )
        return user

class Villaserializer(serializers.ModelSerializer):
    host_id = serializers.ReadOnlyField(source='host_id.full_name')

    class Meta:
        model = Villa
        fields = ['villa_id', 'host_id', 'title', 'city', 'address', 'price_per_night', 'capacity', 'amenities']

class Availabilityserializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['availability_id', 'date', 'is_available']
    
class Reservationserializer(serializers.ModelSerializer):
    guest_id = serializers.ReadOnlyField(source='guest_id.full_name')
    total_price = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Reservation
        fields = ['reservation_id', 'guest_id', 'villa_id', 'check_in', 'check_out', 'total_price', 'status', 'created_at']