from apps.ial.models import (
    IdentityAssuranceLevelDocumentation,
    EVIDENCE_CLASSIFICATIONS)

from rest_framework import serializers, viewsets, permissions
from oauth2_provider.contrib.rest_framework import authentication
from django.contrib.auth import get_user_model
from django.http import Http404
User = get_user_model()

# {
# "description": "NY Medicaid card.",
# "classification": "ONE-SUPERIOR-OR-STRONG+",
# "exp": "2022-01-01",
# "verifier_subject": "876545671054321",
# "note": "A paper copy of the document is on file.",
# "verification_date": "2019-03-04"
# }


class IdentifierSerializer(serializers.ModelSerializer):
    classification = serializers.ChoiceField(source="evidence", choices=EVIDENCE_CLASSIFICATIONS)
    description = serializers.CharField(source="id_verify_description")
    exp = serializers.DateField(source='expires_at')
    verifier_subject = serializers.CharField(source="verifying_user.userprofile.subject", read_only=True)

    class Meta:
        model = IdentityAssuranceLevelDocumentation
        fields = '__all__'
        read_only_fields = ('verifier_subject', )


class IdentifierViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = IdentifierSerializer
    authentication_classes = [authentication.OAuth2Authentication]
    permission_classes = [permissions.DjangoModelPermissions]

    # Set to allow DjangoModelPermissions to determine required model level perms
    queryset = IdentityAssuranceLevelDocumentation.objects.all()

    def get_queryset(self):
        return IdentityAssuranceLevelDocumentation.objects.filter(
            subject_user__userprofile__subject=self.kwargs['user_subject']
        ).all()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            try:
                kwargs['data']['subject_user'] = User.objects.get(userprofile__subject=self.kwargs['user_subject']).pk
                kwargs['data']['verifying_user'] = self.request.user.pk
            except User.DoesNotExist:
                raise Http404
        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
