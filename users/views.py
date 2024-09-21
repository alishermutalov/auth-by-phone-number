from django.shortcuts import render
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, DONE, CODE_VERIFIED, PHOTO_DONE
from . import serializers
from .utils import send_sms_verification_code
from datetime import datetime
# Create your views here.

class SignUpAPIView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.SignUpSerializer
    
    
class ConfirmVerificationCodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request, *args, **kwargs):
        
        user = self.request.user
        code = self.request.data.get('verification_code')
        self.check_verification_code(user, code)
        
        return Response({
            'success':True,
            'auth_status':user.auth_status,
            'access':user.token()['access'],
            'refresh_token':user.token()['refresh_token']
        })
        
    @staticmethod
    def check_verification_code(user, code):
        verification_codes = user.verification_codes.filter(expiration_time__gte = datetime.now(), 
                                                            verification_code = code, is_confirmed = False )
        if not verification_codes.exists():
            raise ValidationError({
                'succss':False,
                'message':'Your verification code is invalid or has expired!'
            })
        else:
            verification_codes.update(is_confirmed=True)
        if user.auth_status not in [DONE, PHOTO_DONE]:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True
    

class GetNewVerificationCodeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        code = user.create_verification_code()
        # send_sms_verification_code(user.phone_number, code) #uncomment, if you set twilio settings
        print(code)
        return Response({
            'success':True,
            'message':'Your verification code has been resent!'
        })
        
    @staticmethod
    def check_verification(user):
        verification_codes = user.verification_codes.filter(
            expiration_time__gte=datetime.now(), 
            is_confirmed=False
        )
        if verification_codes.exists():
            raise ValidationError({
                'message':'Your code has been sent, please wait!'
            })
        
        
class UpdateUserInfoAPIView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.UpdateUserInfoSerializer
    http_method_names = ['put', 'patch']
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):#for PUT http method
        super().update(request, *args, **kwargs)
        return Response({
            'success':True,
            'message':'User information updated successfully!'
        })
        
    def partial_update(self, request, *args, **kwargs): #for PATCH http method
        super().partial_update(request, *args, **kwargs)
        return Response({
            'succss':True,
            'message':'User information updated successfully!'
        })


class SetOrUpdatePhotoAPIView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.SetOrUpdatePhotoSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({
            'success':True,
            'message':'User Photo Set Successfully!'
        })
        

class LoginAPIView(TokenObtainPairView):
    serializer_class = serializers.LoginSerializer
    
    
class LoginRefreshAPIView(TokenRefreshView):
    serializer_class = serializers.RefreshTokenSerializer
    

class LogoutAPIView(APIView):
    serializer_class = serializers.LogoutSerializer
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'success':True,
                'message':'You successfully logged out!'
            }, status=205)
        except TokenError:
            return Response(status=400)


class ForgotPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.ForgotPasswordSerializer
    
    def post(self,request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        
        return Response({
            'success':True,
            'message':'Verification code sent successfully!',
            'access':user.token()['access'],
            'refresh':user.token()['refresh_token'],
        }, status=200)
        

class ResetPasswordAPIView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = serializers.ResetPasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        user = self.get_object()
        
        return Response({
            'success':True,
            'message':'Pasword Set successfully!',
            'access':user.token()['access'],
            'refresh':user.token()['refresh_token'],
        })
    