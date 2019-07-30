from django_filters import rest_framework as filters
from rest_framework import serializers, viewsets, permissions
from rest_framework.exceptions import ValidationError
from oauth2_provider.contrib.rest_framework import authentication
from django.http import JsonResponse
import logging
from django.contrib.sessions.models import Session
from oauth2_provider.decorators import protected_resource
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.accounts.models import (
    UserProfile,
    SEX_CHOICES,
)
from apps.oidc.claims import get_claims_provider

logger = logging.getLogger('verifymyidentity_.%s' % __name__)


User = get_user_model()
ClaimsProvider = get_claims_provider()


class UserFilter(filters.FilterSet):
    first_or_last_name = filters.CharFilter(method='filter_first_or_last_name')

    def filter_first_or_last_name(self, queryset, name, value):
        """Filter by the UserProfile's User's first_name or last_name."""
        return queryset.filter(
            Q(user__first_name__icontains=value) | Q(
                user__last_name__icontains=value)
        )

    class Meta:
        model = UserProfile
        fields = ['first_or_last_name']


class UserSerializer(serializers.Serializer):
    preferred_username = serializers.CharField(
        max_length=255, source='user.username')
    given_name = serializers.CharField(
        max_length=255, source='user.first_name')
    family_name = serializers.CharField(
        max_length=255, source='user.last_name')
    gender = serializers.ChoiceField(choices=SEX_CHOICES, source='sex')
    password = serializers.CharField(
        max_length=255, write_only=True, source='user.password')
    birthdate = serializers.DateField(source='birth_date')
    nickname = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255, source='user.email')
    phone_number = serializers.CharField(
        max_length=255, source='mobile_phone_number', required=False)
    picture = serializers.ImageField(required=False)

    def create(self, validated_data):
        # raise Exception(validated_data)
        user_data = validated_data.get('user', {})
        if User.objects.filter(username=user_data['username']).exists():
            raise ValidationError(
                'Could not create user with that username. Please choose another.', code=400)
        # Force upper/lover cases
        first_name = user_data.get('first_name').upper().strip()
        last_name = user_data.get('last_name').upper().strip()
        username = user_data.get('username').lower().strip()
        email = user_data.get('email').lower().strip()
        user_data['first_name'] = first_name
        user_data['last_name'] = last_name
        user_data['email'] = email
        user_data['username'] = username

        user = User.objects.create(**user_data)

        # We must use the set_password() method to set the user's password
        user.set_password(user_data['password'])
        user.save()

        validated_data['user'] = user
        return UserProfile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If the user's password is being set, we must use the set_password()
        # method to set it
        if user_data.get('password'):
            instance.user.set_password(user_data.pop(
                'password'))   # good-bye, raw password
            instance.user.save()

        instance.save()

        for attr, value in user_data.items():  # don't set raw password
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
    filterset_class = UserFilter
    authentication_classes = [authentication.OAuth2Authentication]
    permission_classes = [permissions.DjangoModelPermissions]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@require_GET
@protected_resource()
def logout_user(request):
    # A remote API call for logging out the user
    user = request.resource_owner
    delete_all_sessions_for_user(user)
    data = {"status": "ok",
            "message": "%s sessions removed. Remote logout." % (user)}
    logger.info("$s logged out remotely.", user)
    return JsonResponse(data)


def delete_all_sessions_for_user(user):
    user_sessions = []
    all_sessions = Session.objects.all()
    for session in all_sessions:
        session_data = session.get_decoded()
        if str(user.pk) == str(session_data.get('_auth_user_id')):
            user_sessions.append(session.pk)
    Session.objects.filter(pk__in=user_sessions).delete()
    return user_sessions
