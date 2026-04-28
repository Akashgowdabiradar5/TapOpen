from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, SendOTPView, VerifyOTPView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/send/', SendOTPView.as_view(), name='otp_send'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp_verify'),
]
