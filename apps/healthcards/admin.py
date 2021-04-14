from django.contrib import admin
from .models import SmartHealthJWKS, SmartHealthCard

__author__ = "Alan Viars"



class SmartHealthJWKSAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'kid')
    search_fields = ['kid', 'nickname']

admin.site.register(SmartHealthJWKS, SmartHealthJWKSAdmin)


class SmartHealthCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'updated')
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__username',
        'user__email']
    raw_id_fields = ("user", )

admin.site.register(SmartHealthCard, SmartHealthCardAdmin)
