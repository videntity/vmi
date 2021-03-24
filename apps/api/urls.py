from django.urls import include, path
from rest_framework_nested import routers
from .views import (
    UserViewSet,
    IdentifierViewSet,
    AddressViewSet,
    logout_user

)

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)

owned_by_user_router = routers.NestedSimpleRouter(
    router, r'user', lookup='user')
owned_by_user_router.register(
    r'id-assurance', IdentifierViewSet, basename='identifier')
owned_by_user_router.register(r'address', AddressViewSet, basename='address')

v1 = [
    path('', include(router.urls)),
    path('', include(owned_by_user_router.urls)),
    path('remote-logout', logout_user, name="remote_logout"),
]

urlpatterns = [
    path('v1/', include(v1)),
]
