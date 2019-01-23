from django.contrib import admin
from .models import SMSDevice


@admin.register(SMSDevice)
class SMSDeviceAdmin(admin.ModelAdmin):
    pass
