from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from .models import Profile, OTPVerification
from rest_framework_simplejwt.tokens import RefreshToken


class SendOTPView(APIView):
    """
    Send an OTP to an email or phone number.
    Body: { "identifier": "test@example.com", "otp_type": "EMAIL" }
    For phone OTPs, the code is printed to the console (dev mode).
    """
    def post(self, request):
        identifier = request.data.get('identifier', '').strip()
        otp_type = request.data.get('otp_type', 'EMAIL').upper()

        if not identifier:
            return Response({'error': 'identifier is required'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_type not in ('EMAIL', 'PHONE'):
            return Response({'error': 'otp_type must be EMAIL or PHONE'}, status=status.HTTP_400_BAD_REQUEST)

        code = OTPVerification.generate_otp()
        OTPVerification.objects.create(identifier=identifier, otp_type=otp_type, code=code)

        if otp_type == 'EMAIL':
            send_mail(
                subject='Your Resumify Verification OTP',
                message=f'Your OTP code is: {code}\nThis code expires in 10 minutes.',
                from_email='noreply@resumify.com',
                recipient_list=[identifier],
                fail_silently=False,
            )
        else:
            # Phone OTP: in dev mode, print to console; in production, integrate an SMS gateway here.
            print(f'[Resumify SMS OTP] Send to {identifier}: {code}')

        return Response({'message': f'OTP sent to {identifier}'}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    Verify a previously sent OTP.
    Body: { "identifier": "test@example.com", "otp_type": "EMAIL", "code": "123456" }
    """
    def post(self, request):
        identifier = request.data.get('identifier', '').strip()
        otp_type = request.data.get('otp_type', 'EMAIL').upper()
        code = request.data.get('code', '').strip()

        if not all([identifier, otp_type, code]):
            return Response({'error': 'identifier, otp_type and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        record = OTPVerification.objects.filter(
            identifier=identifier,
            otp_type=otp_type,
            code=code,
            is_verified=False,
        ).order_by('-created_at').first()

        if not record:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        if record.is_expired():
            return Response({'error': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        record.is_verified = True
        record.save()

        return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            role = 'SEEKER'
            if hasattr(user, 'profile'):
                role = user.profile.role

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        role = request.data.get('role', 'SEEKER')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        phone_number = request.data.get('phone_number', '').strip()
        address = request.data.get('address', '').strip()

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'An account with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        Profile.objects.create(
            user=user,
            role=role,
            phone_number=phone_number,
            address=address,
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': role
        }, status=status.HTTP_201_CREATED)
