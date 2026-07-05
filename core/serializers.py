from rest_framework import serializers
from .models import User

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