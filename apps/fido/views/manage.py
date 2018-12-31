from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import authentication
from rest_framework import pagination
from ..models import AttestedCredentialData


class DeviceSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%b %d, %Y, %I:%M %p')

    class Meta:
        model = AttestedCredentialData
        fields = ('id', 'name', 'created_at',)


class ManageViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    A simple ViewSet for viewing and editing devices.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceSerializer

    pagination_class = pagination.LimitOffsetPagination
    pagination_class.default_limit = 10

    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer,)
    template_name = "list.html"

    def get_queryset(self):
        queryset = AttestedCredentialData.objects.filter(user=self.request.user).all()
        return queryset


class DetailViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """
    A simple ViewSet for viewing and editing devices.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceSerializer

    renderer_classes = (renderers.JSONRenderer, renderers.TemplateHTMLRenderer,)

    template_name = "detail.html"

    def get_queryset(self):
        queryset = AttestedCredentialData.objects.filter(user=self.request.user).all()
        return queryset
