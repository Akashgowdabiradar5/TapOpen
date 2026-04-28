from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta


class Profile(models.Model):
    ROLE_CHOICES = (
        ('SEEKER', 'Job Seeker'),
        ('COMPANY', 'Company'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='SEEKER')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class OTPVerification(models.Model):
    OTP_TYPE_CHOICES = (
        ('EMAIL', 'Email'),
        ('PHONE', 'Phone'),
    )
    identifier = models.CharField(max_length=255)  # email address or phone number
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.otp_type} OTP for {self.identifier}"
