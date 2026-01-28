from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError




class SignUpSerializer(serializers.ModelSerializer):
    confirm_pass = serializers.CharField(write_only=True)
    class Meta:
        model = User
        feilds = ['username', 'first_name', 'password', 'confrim_pass']
        
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_pass = attrs.get('confirm_pass')
        if password is None or confirm_pass is None or password != confirm_pass:
            raise ValidationError({'suscess': False, 'messgae': "Parollar toliq kiritilmagan"})
        return attrs
    
    
    def create(self, validated_data):
        validated_data.pop('confirm_pass')
        user = User.objects.create_user(**validated_data)
        return user
    
    
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        mode = User
        fields = ['first_name', 'username']
        
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        mode = User
        fields = ['first_name', 'username']