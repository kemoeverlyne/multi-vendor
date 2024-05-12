from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from userauths.models import User, Profile
from userauths.serializer import MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer

import random
import shortuuid

from .serializer import ProfileSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = RegisterSerializer


def generate_otp(length=7):
    uuid_key = shortuuid.uuid()
    unique_key = uuid_key[:6]
    return unique_key


class PasswordResetEmailVerificationView(generics.RetrieveAPIView):
    permission_classes = [AllowAny,]
    serializer_class = UserSerializer
    
    def get_object(self):
        email = self.kwargs.get('email')
        user = User.objects.get(email=email)

        if user:
            otp = generate_otp()
            user.otp = otp
            user.save()

            uidb64 = user.pk
            otp = user.otp

            link = f"http://localhost:5173/create-new-password?otp={otp}&uidb64={uidb64}"
            print("link ======", link)

            # send email
            
        return user
    

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = [AllowAny,]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        payload = request.data

        try:
            otp = payload.get('otp')
            uidb64 = payload.get('uidb64') 
            password = payload.get('password')  
            user = User.objects.get(otp=otp, id=int(uidb64))
   
        except User.DoesNotExist:
            # Handle user not found
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Handle any other exceptions
            return Response({'message': f'Unexpected error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Set the new password for the user
        user.set_password(password)
        user.otp = ""
        user.save()

        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny,]
    serializer_class = ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)

        return profile
    


    



