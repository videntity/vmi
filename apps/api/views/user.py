from rest_framework import serializers, viewsets, permissions
from oauth2_provider.contrib.rest_framework import authentication

from django.contrib.auth import get_user_model
from apps.accounts.models import (
    UserProfile,
    GENDER_CHOICES,
)
from apps.oidc.claims import get_claims_provider
# {
#     "username": "james",
#     "given_name": "James",
#     "family_name": "Kirk",
#     "gender": "male",
#     "password": "tree garden jump fox",
#     "birthdate": "1952-01-03",
#     "nickname": "Jim",
#     "phone_number": "+15182345678",
#     "email": "jamess@example.com"
# }
User = get_user_model()
ClaimsProvider = get_claims_provider()


class UserSerializer(serializers.Serializer):
    preferred_username = serializers.CharField(max_length=255, source='user.username')
    given_name = serializers.CharField(max_length=255, source='user.first_name')
    family_name = serializers.CharField(max_length=255, source='user.last_name')
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, source='sex')
    password = serializers.CharField(max_length=255, write_only=True, source='user.password')
    birthdate = serializers.DateField(source='birth_date')
    nickname = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255, source='user.email')
    phone_number = serializers.CharField(max_length=255, source='mobile_phone_number')

    def create(self, validated_data):
        # raise Exception(validated_data)
        user_data = validated_data.get('user', {})
        user = User.objects.create(**user_data)

        validated_data['user'] = user
        return UserProfile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        instance.user.save()

        return instance

    def to_representation(self, instance):
        cp = ClaimsProvider(user=instance.user)
        return cp.get_claims()


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "subject"
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.OAuth2Authentication]
    permission_classes = [permissions.DjangoModelPermissions]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
