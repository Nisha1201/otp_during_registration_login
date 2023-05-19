from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer
from django.contrib.auth import get_user_model, authenticate
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client
from random import randint

User = get_user_model()

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate OTP
        otp = str(randint(1000, 9999))

        # Save the OTP in cache with a key using the phone number
        cache_key = f"otp_{user.phone_number}"
        cache.set(cache_key, otp, timeout=300)  # Set a timeout for the OTP (e.g., 5 minutes)

        # Send OTP via SMS using Twilio
        account_sid = 'AC9124c9f9d6ebad6bffa281e0d3604bb4'
        auth_token = '611762efc304d9e767ccafd3d4203990'
        twilio_number = '+16073604837' # Replace with your Twilio phone number
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f'Your OTP for registration: {otp}',
            from_=twilio_number,
            to=user.phone_number
        )

        # Return success response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_verified:
                # Generate OTP
                otp = str(randint(1000, 9999))
                
                # Save the OTP in cache with a key using the phone number
                cache_key = f"otp_{user.phone_number}"
                cache.set(cache_key, otp, timeout=300)  # Set a timeout for the OTP (e.g., 5 minutes)
                
                # Send OTP via SMS using Twilio
                account_sid = 'AC9124c9f9d6ebad6bffa281e0d3604bb4'
                auth_token = '611762efc304d9e767ccafd3d4203990'
                twilio_number = '+16073604837'  # Replace with your Twilio phone number
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    body=f'Your OTP for login: {otp}',
                    from_=twilio_number,
                    to=user.phone_number
                )
                
                # Return success response
                return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not verified'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_otp(request):
    phone_number = request.data.get('phone_number')
    otp = request.data.get('otp')
    
    # Retrieve the stored OTP from cache
    cache_key = f"otp_{phone_number}"
    stored_otp = cache.get(cache_key)
    
    if stored_otp == otp:
        # Retrieve the user based on the phone number
        user = User.objects.get(phone_number=phone_number)
        user.is_verified = True
        user.save()
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh)
,
            'access': str(refresh.access_token),
        }
        
        # Return the token in the response
        return Response(token, status=status.HTTP_200_OK)
        # return Response(status=status.HTTP_200_OK)
    
    return Response({'error': 'Invalid OTP'}, status=status.HTTP_401_UNAUTHORIZED)