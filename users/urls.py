from django.urls import path
from .views import SignUpAPIView, ConfirmVerificationCodeAPIView,\
    GetNewVerificationCodeAPIView, SetOrUpdatePhotoAPIView,\
        UpdateUserInfoAPIView, LoginAPIView, LoginRefreshAPIView, LogoutAPIView,\
            ForgotPasswordAPIView, ResetPasswordAPIView


urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', LoginRefreshAPIView.as_view(), name='login-refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('verify/', ConfirmVerificationCodeAPIView.as_view(), name='verify'),
    path('verify/resend/', GetNewVerificationCodeAPIView.as_view(), name='resend-verify'),
    path('update-user/', UpdateUserInfoAPIView.as_view(), name='update-user'),
    path('update-user-photo/', SetOrUpdatePhotoAPIView.as_view(), name='update-user-photo'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    
]
