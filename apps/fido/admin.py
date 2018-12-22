from django.contrib import admin
from .models import AttestedCredentialData

__author__ = "Alan Viars"


class AttestedCredentialDataAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__username',
        'user__email']
    raw_id_fields = ("user", )


admin.site.register(AttestedCredentialData, AttestedCredentialDataAdmin)
