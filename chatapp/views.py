import pyotp
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from .models import MyUser,MyUserProfile,OtpModel
from .serializers import MyUserSerializer,MyUserProfileSerializer,OtpSerializer,FCMdeviceSerializer
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from django.core.mail import send_mail
from django.conf import settings
from fcm_django.models import FCMDevice
from django.utils import timezone
from firebase_admin.messaging import Message, Notification






def generate_otp(user_id):
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    try:
        otp_model = OtpModel.objects.get(otp_myuser=user_id)
        otp_model.otp_code = otp
        otp_model.save()
    except OtpModel.DoesNotExist:
        otp_serializer = OtpSerializer(data={'otp_myuser':user_id,'otp_code':otp})
        otp_serializer.is_valid(raise_exception=True)
        otp_serializer.save()

    return otp


class RegisterAPIView(APIView):

    def post(self, request):
        serializer = MyUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        otp = generate_otp(user.id)
        send_mail(
            'OTP verification',
            f'User Registered successfully\nPlease verify the otp to log in\nOTP:{otp}(valid for 1 minute)',
            settings.EMAIL_HOST_USER, [user.email]
        )
        return Response({
            "message":"User Registered successfully","OTP": "please check mail for otp",
            "status" : status.HTTP_201_CREATED
                },status=201
            )  
                         
class RegenrateOtpAPIView(APIView):
    def post(self, request):
        user = get_object_or_404(MyUser,email=request.data.get('email'))
        otp = generate_otp(user.id)
        send_mail(
            'OTP verification',
            f'User Registered successfully\nPlease verify the otp to log in\nOTP:{otp}(valid for 1 minute)',
            settings.EMAIL_HOST_USER, [user.email]
        )
        return Response({
            "message":"otp regenerated successfully,Please check mail for otp",
            "status":status.HTTP_200_OK
        })

class VerifyOtpAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_otp = request.data.get('otp')
        user = get_object_or_404(MyUser, email=email)
        model_otp = get_object_or_404(OtpModel, otp_myuser=user)
        #model_otp = get_object_or_404(OtpModel.objects.filter(otp_myuser=user).order_by('-created_at')[:1])
        
        if model_otp.otp_code != user_otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        time_elapsed = timezone.now() - model_otp.updated_at
        if time_elapsed.total_seconds() > 60:
            return Response({'error': 'OTP has expired..!!, Please Regenerate the otp','time':time_elapsed}, status=status.HTTP_400_BAD_REQUEST)
    
        user.is_active = True
        user.save()
        return Response({'message': 'OTP verification successful..',"time":time_elapsed}, status=status.HTTP_200_OK) 
            
class LoginAPIView(APIView):
    
    def post(self, request): 

        email = request.data.get("email")
        password = request.data.get("password")
        if user := authenticate(username=email, password=password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                "status":status.HTTP_200_OK, 
                "massage":"User Logged in succesfully..",
                "Token": {'refresh':str(refresh),'access_token':str(refresh.access_token)}
                })
        return Response({
                "error": "Wrong Credentials",
                "status":status.HTTP_400_BAD_REQUEST,
                },status=400)

class LogoutAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated] 
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(token=refresh_token)
        token.blacklist()
        return Response({
                "message": "User Logout Successfully",
                "status": status.HTTP_200_OK
                })
        
class MyUserDataAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer      
       
class MyUserProfileAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        try:
            data = MyUserProfile.objects.get(myuser=request.user.id)
        except MyUserProfile.DoesNotExist as e:
            raise Http404("Details not found") from e
        serializer = MyUserProfileSerializer(data)
        return Response(serializer.data) 


    def post(self,request):
        request.data['myuser'] = request.user.id
        serializer = MyUserProfileSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'status' : status.HTTP_201_CREATED,
            'message': 'UserProfile Created Successfully',
            'Profile': serializer.data
        })

    
    def put(self, request, format=None):
        profile_to_update = MyUserProfile.objects.get(myuser=request.user.id)
        serializer = MyUserProfileSerializer(instance = profile_to_update, data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            'message': 'User Updated Successfully',
            'data': serializer.data
        }) 

class MyUserCreateFCMdevicesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        data = request.data    #registration id and type('android','web','ios')
        data['user'] = request.user.id
        serializer = FCMdeviceSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "device registered successfully.",
            "info": serializer.data 
        })    

class MyUserFCMdevicesAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        try:
            return FCMDevice.objects.filter(user=self.request.user)
        except FCMDevice.DoesNotExist as e:
            raise e
    serializer_class = FCMdeviceSerializer

class PushNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        title = request.data.get("title")
        message = request.data.get("message")
        notification = Notification(title=title, body=message)
        message = Message(notification=notification, data={"timestamp":timezone.now().isoformat()})
        try:
            devices = FCMDevice.objects.filter(user = request.user)
            for device in devices:
                device.send_message(message)
            return Response({
                "message":"Push notification sent successfully.",
                "notification": {"title":notification.title,"body":notification.body},
                "devices" : [i[-1] for i in devices.values_list()]
            })
        except FCMDevice.DoesNotExist as e:
            raise e

