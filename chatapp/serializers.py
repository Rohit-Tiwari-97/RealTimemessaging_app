from rest_framework import serializers
from chatapp.models import MyUser,MyUserProfile,OtpModel
from fcm_django.models import FCMDevice




class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id','email','userRole','created_at','is_active','is_admin']


class MyUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUserProfile   
        fields = '__all__'

class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpModel
        fields = '__all__'  

class FCMdeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = '__all__'

