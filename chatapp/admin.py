from django.contrib import admin
from chatapp.models import MyUser,MyUserProfile,OtpModel

admin.site.register(MyUser)
admin.site.register(MyUserProfile)
admin.site.register(OtpModel)
