from apps.accounts.models import (
    Address,
)

from rest_framework import serializers, viewsets, permissions
from oauth2_provider.contrib.rest_framework import authentication
from django.contrib.auth import get_user_model
from django.http import Http404
User = get_user_model()

# {
#     "formatted": "837 State St.\n Schenectady, NY 12307",
#     "street_address": "837 State St.",
#     "locality": "Schenectady",
#     "region": "NY",
#     "postal_code": "12307",
#     "country": "US"
# }


class AddressSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(source='street_1')
    locality = serializers.CharField(source='city')
    region = serializers.CharField(source='state')
    postal_code = serializers.CharField(source='zipcode')

    class Meta:
        model = Address
        fields = ('uuid', 'street_address', 'locality', 'region', 'postal_code', 'country', 'formatted', 'user', )
        read_only_fields = ('formatted', )
        write_only_fields = ('user', )


class AddressViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = AddressSerializer
    authentication_classes = [authentication.OAuth2Authentication]
    permission_classes = [permissions.DjangoModelPermissions]

    # Set to allow DjangoModelPermissions to determine required model level perms
    queryset = Address.objects.all()

    def get_queryset(self):
        return Address.objects.filter(
            user__userprofile__subject=self.kwargs['user_subject']
        ).all()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            try:
                kwargs['data']['user'] = User.objects.get(userprofile__subject=self.kwargs['user_subject']).pk
            except User.DoesNotExist:
                raise Http404
        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
