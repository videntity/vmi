from django.urls import include, path
from rest_framework_nested import routers
from .views import (
    UserViewSet,
    IdentifierViewSet,
    AddressViewSet,
)

router = routers.SimpleRouter()
router.register(r'user', UserViewSet)

owned_by_user_router = routers.NestedSimpleRouter(router, r'user', lookup='user')
owned_by_user_router.register(r'id-assurance', IdentifierViewSet, base_name='identifier')
owned_by_user_router.register(r'address', AddressViewSet, base_name='address')

v1 = [
    path('', include(router.urls)),
    path('', include(owned_by_user_router.urls)),
]

urlpatterns = [
    path('v1/', include(v1)),
]
