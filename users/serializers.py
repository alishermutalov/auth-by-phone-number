from typing import Any, Dict
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from .models import NEW, User, CODE_VERIFIED, DONE, PHOTO_DONE
from .utils import check_phone_number, send_sms_verification_code


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id',
            'phone_number',
            'auth_status'
        )
    
    def validate(self, attrs):
        super().validate(attrs)
        phone_number = attrs.get('phone_number', None)
        if phone_number is not None:
            if check_phone_number(phone_number):
                if User.objects.filter(phone_number=phone_number).exists():
                    raise ValidationError({
                        'success':False,
                        'message':'This phone number is alredy taken'
                    })
                attrs = {
                    'phone_number': phone_number,
                }
          
        return attrs
    
    def create(self, validated_data):
        user = super().create(validated_data)
        code = user.create_verification_code()
        print(code)
        #send_sms_verification_code(user.phone_number, code) #It's not working if you don't have twilio subscription!
        user.save()
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data
    

class UpdateUserInfoSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        password = attrs.get('password', None)
        confirm_password = attrs.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError({
                'message':'Password and Confirmation password do not match!'
            })    
        if password:
            validate_password(password)    
        return attrs
    
    def validate_username(self, username):
        if User.objects.filter(username__iexact=username):
            raise ValidationError({
                "message":"This username alredy taken!"
            })
        
        if len(username)<4 or len(username)>32:
            raise ValidationError({
                'message':'Username must be more than 4 characters and less than 32 characters'
            })
        if username.isdigit():
            raise ValidationError({
                'message':'This username is entirely numeric'
            })
        
        return username
            
    def validate_first_name(self, first_name):
        if len(first_name)<1 or len(first_name)>50:
            raise ValidationError({
                'message':'First name must be more than 4 characters and less than 32 characters'
            })
        if first_name.isdigit():
            raise ValidationError({
                'message':'This first name is entirely numeric'
            })
        
        return first_name   
    
    def validate_last_name(self, last_name):
        if len(last_name)<1 or len(last_name)>50:
            raise ValidationError({
                'message':'last name must be more than 4 characters and less than 32 characters'
            })
        if last_name.isdigit():
            raise ValidationError({
                'message':'This last name is entirely numeric'
            })
        
        return last_name 
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        
        return instance
    

class SetOrUpdatePhotoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('photo',)
        
    def validate(self, attrs):
        photo_size = attrs['photo'].size
        max_size = 10*1024*1024 #10MB
        if photo_size>max_size:
            raise ValidationError({
                'message':'Image file is too large. Maximum allowed size is 10MB.'
            })
        return attrs
    
    def update(self, instance, validated_data):
        instance.photo = validated_data.get('photo', instance.photo)
        if instance.auth_status == DONE:
            instance.auth_status = PHOTO_DONE
        instance.save()
        
        return instance
    

class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['user_input']=serializers.CharField(required=True)
        self.fields['username']=serializers.CharField(required=False, read_only=True)
        
    def auth_validate(self,data):
        user_input = data.get('user_input')
        
        if check_phone_number(user_input):
            user = User.objects.filter(phone_number=user_input).first()
            username = user.username
        elif User.objects.filter(username=user_input).first() is not None:
            user = User.objects.filter(username=user_input).first()
            username= user.username
        else:
            raise NotFound("User not found!")
        
        auth_kwargs = {
            self.username_field : username,
            'password' : data['password']
        }
        
        if user is not None and user.auth_status in [CODE_VERIFIED, NEW]:
            raise ValidationError({
                'message':'You are not fully registered yet!'
            })
        user = authenticate(**auth_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError({
                'message':'Sorry, your username or password incorrect, please try again!'
            })
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        self.auth_validate(attrs)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            PermissionDenied("You can't login. You don't have permission.")
        attrs = self.user.token()
        attrs['auth_status']=self.user.auth_status    
        attrs['full_name']=self.user.full_name    
        return attrs
    

class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        acces_token_instance = AccessToken(data["access"])
        user_id = acces_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    

class ForgotPasswordSerializer(serializers.Serializer):
    """
    when the user uses this function, an SMS code will be sent to him.
    This code can be checked through the /verify/ endpoint. 
    Briefly: /forgot-password/ -> It will send verification code. 
    You need to send verification code to /verify/ 
    endpoint. -> returns True (if True, returns 'access',
    'refresh_token' and etc.) or False
    """
    phone_number = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs.get('phone_number') is None:
            raise ValidationError({
                'message':'You must enter phone number'
            })
        user = User.objects.filter(phone_number=attrs['phone_number']).first()
        if user is None:
            raise NotFound("User not found with this phone number!")
        code = user.create_verification_code()
        # send_sms_verification_code(user.phone_number, code) #if you don't have twilio subscription it doesn't work
        print(code)
        attrs['user']=user
        return attrs
    


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = (
            'password',
            'confirm_password',
        )
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError({
                "message":"Password and Confirm Password didn't match!"
            })
        if password:
            validate_password(password)
        return attrs
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password') # .pop() Retrieves and removes 'password' from validated_data
        instance.set_password(password)
        instance.save()
        return super().update(instance, validated_data)