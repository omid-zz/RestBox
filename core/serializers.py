from rest_framework import serializers
from .models import User, Villa, Reservation

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
    host = serializers.ReadOnlyField(source='host.full_name')

    class Meta:
        model = Villa
        fields = ['id', 'host', 'title', 'city', 'address', 'price_per_night', 'capacity', 'amenities']
    
class Reservationserializer(serializers.ModelSerializer):
    guest = serializers.ReadOnlyField(source='guest.full_name')
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Reservation
        fields = ['id', 'guest_id', 'villa_id', 'check_in', 'check_out', 'total_price', 'status', 'created_at']
    
    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError("Check-in should be before check-out")
        return data