from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import SignUpSerializer, ProfileUpdateSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from .utility import send_simple_email, check_email
import random
from .models import VerifyCode
from django.utils import timezone
# Create your views here.


class SignUpView(APIView):
    permission_classes = [AllowAny, ]
    serilizer_class = SignUpSerializer
    queryset = User
    
    def post(self, requset):
        serializer = self.serilizer_class(data=requset.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        data = {
            'status': status.HTTP_201_CREATED,
            'username': serializer.data['username'],
            'message': 'Akkount yaratildi'
        }
        return Response(data=data)


class LoginView(APIView):
    permission_classes = [AllowAny, ]
    
    def post(self,request):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        
        user = User.objects.filter(username=username).first()
        if user is None:
            raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Bizda bunaqa user mavjud emas'})
        user = user.check_password(password)
        if not user:
            raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Parol xato'})
        user = authenticate(username=username, password=password)
        
        if user is None:
            raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Bizda bunaqa user mavjud emas'})
        refresh = RefreshToken.for_user(user)
        
        data = {
            'status': status.HTTP_200_OK,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Siz tzizmga kirdingiz'
        }
        return Response(data=data)


class LogoutView(APIView):
    permissions_classes = [permissions.IsAuthenticated, ]
    def post(self, request):
        refresh = self.request.data.get('refresh_token')
        refresh = RefreshToken(refresh)
        refresh.blacklist()
        data = {
            'succes': True,
            'message': 'Siz tizimdan chiqdingiz'
        }
        return Response(data)
    

class ProfileView(APIView):
    def get(self,request):
        user = self.request.user
        data = {
            'status': status.HTTP_200_OK,
            'username': user.username,
            'first_name': user.first_name
        }
        return Response(data)
    
    
class ProfileUpdateView(APIView):
    def post(self,request):
        serializer = ProfileUpdateSerializer(instance =request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            
            data = {
                'status': status.HTTP_200_OK,
                'username': user.username,
                'first_name': user.first_name,
                'message': 'Malumotlar yangilandi'
            }
            return Response(data)
        data = {
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'ERROR'
            }
        return Response(data)
    
    
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'message': 'Eski parol xato', 'status':status.HTTP_400_BAD_REQUEST})
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Parol yangilandi', 'status':status.HTTP_200_OK})
    
    

class ForgotView(APIView):
    permission_classes = [AllowAny,]
    
    def post(self, request):
        email = self.request.data.get('email')
        email = check_email(email)
        if email:
            user = User.objects.filter(email=email).first()
            if user is None:
                raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Bizda bunaqa user mavjud emas'})
            code = random.randint(1000, 9999)
            VerifyCode.objects.create(
                user=user,
                code=code,
        )
            send_simple_email(user.email, code)
            data = {
                'status': status.HTTP_200_OK,
                'message': 'Kod emailga yuborildi'
            }
            return Response(data)
        data = {
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Xatolik'
        }
        return Response(data)
    
class ResetCodeView(APIView):
    permission_classes = [AllowAny,]
    
    def post(self, request):
        email = self.request.data.get('email')
        code = self.request.data.get('code')
        new_password = self.request.data.get('new_password')
        
        email = check_email(email)
        if email:
            user = User.objects.filter(email=email).first()
            if user is None:
                raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Bizda bunaqa user mavjud emas'})
            verify_code = VerifyCode.objects.filter(user=user, code=code, is_active=False).order_by('-id').first()
            if verify_code is None:
                raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Kod xato'})
            if verify_code.expiration_time < timezone.now():
                raise ValidationError({'status': status.HTTP_400_BAD_REQUEST,'message':'Kodning muddati tugagan'})
            verify_code.is_active = True
            verify_code.save()
            
            if new_password:
                user.set_password(new_password)
                user.save()
                data = {
                    'status': status.HTTP_200_OK,
                    'message': 'Parol yangilandi'
                }
            else:
                data = {
                    'status': status.HTTP_200_OK,
                    'message': 'Kod tasdiqlandi'
            }
            return Response(data)
        data = {
            'status': status.HTTP_400_BAD_REQUEST,
            'message': 'Xatolik'
        }
        return Response(data)