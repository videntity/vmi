from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import serializers
from ..models import AttestedCredentialData


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttestedCredentialData
        fields = '__all__'


class ManageViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    A simple ViewSet for viewing and editing devices.
    """
    queryset = AttestedCredentialData.objects.all()
    serializer_class = DeviceSerializer
