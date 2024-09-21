import uuid
import random
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import FileExtensionValidator
from rest_framework.exceptions import NotFound
# Create your models here.

ORDINARY_USER, ADMIN = 'ordinary_user', 'admin'
NEW, CODE_VERIFIED, DONE, PHOTO_DONE= "new", "code_verified","done", "photo_done"


class User(AbstractUser):
    USER_ROLES = ((ORDINARY_USER, ORDINARY_USER),
                  (ADMIN, ADMIN),) #these choices fields can be changed according to requirements
    AUTH_STATE = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=155, choices=USER_ROLES, default=ORDINARY_USER)
    phone_number = models.CharField(max_length=15, unique=True)
    auth_status = models.CharField(max_length=155, choices=AUTH_STATE, default=NEW)
    photo = models.ImageField(upload_to='users/avatar/', blank=True, null=True)
    
    def __str__(self) -> str:
        return f"{self.username}"
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            raise NotFound("Full name not found!")
    
    def create_verification_code(self):
        verification_code = f"{random.randint(100000, 999999)}" 
        UserConfirmation.objects.create(
            user_id = self.id,
            verification_code = verification_code
        )

        return verification_code
    
    def check_username(self):
        if not self.username:
            generated_username = f"user-{uuid.uuid4().__str__().split('-')[-1]}"
            while True:
                try:
                    if not User.objects.filter(username=generated_username).exists():
                        self.username = generated_username
                        break  
                    else:
                        generated_username += str(random.randint(0, 9))
                except Exception as e:
                    raise e
    
    def check_pass(self):
        if not self.password:
            password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = password
    
    def hash_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
    
    def token(self):
        refresh_token = RefreshToken.for_user(self)
        return {
            'access': str(refresh_token.access_token),
            'refresh_token': str(refresh_token)
        }
    
    def clean(self) -> None:
        self.check_username()
        self.check_pass()
        self.hash_password()
        
    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)
        
    
class UserConfirmation(models.Model):
    verification_code = models.CharField(max_length=6,)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    expiration_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)    
    
    def __str__(self) -> str:
        return f"user-{self.user}"
    
    def save(self, *args, **kwargs) -> None:
        self.expiration_time = datetime.now()+timedelta(minutes=2)
        super(UserConfirmation, self).save(*args, **kwargs)