from django.contrib import admin
from .models import (IdentityAssuranceLevelDocumentation)

# Copyright Videntity Systems Inc.

__author__ = "Alan Viars"


class IdentityAssuranceLevelDocumentationAdmin(admin.ModelAdmin):
    list_display = ('subject_user', 'verifying_user', 'level', 'created_at')
    search_fields = [
        'subject_user__first_name',
        'subject_user__last_name',
        'subject_user__username',
        'verifying_user__first_name',
        'verifying_user__last_name',
        'verifying_user__username']
    raw_id_fields = ("subject_user", 'verifying_user')


admin.site.register(
    IdentityAssuranceLevelDocumentation,
    IdentityAssuranceLevelDocumentationAdmin)
