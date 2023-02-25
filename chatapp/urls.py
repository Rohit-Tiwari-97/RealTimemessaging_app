from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegisterAPIView,
VerifyOtpAPIView,
RegenrateOtpAPIView,
LoginAPIView,
MyUserDataAPIView,
MyUserProfileAPIView,
MyUserCreateFCMdevicesAPIView,
MyUserFCMdevicesAPIView,
PushNotificationView,
LogoutAPIView,
)


urlpatterns = [
    path('register/', RegisterAPIView.as_view()), 
    path('otpverification/', VerifyOtpAPIView.as_view()),   
    path('regenerateotp/', RegenrateOtpAPIView.as_view()),
    path('login/', LoginAPIView.as_view()), 
    path('refreshtoken/', TokenRefreshView.as_view()),        
    path('users/', MyUserDataAPIView.as_view()),
    path('userprofile/', MyUserProfileAPIView.as_view()),
    path('createdevices/', MyUserCreateFCMdevicesAPIView.as_view()),
    path('userdevices/', MyUserFCMdevicesAPIView.as_view()),
    path('pushnoti/', PushNotificationView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
]