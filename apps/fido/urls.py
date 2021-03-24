from django.urls import path, include
from rest_framework import routers
from .views import (
    register,
    verify,
    manage,
)

router = routers.SimpleRouter()
# Post Edit route.
router.routes[2].mapping['post'] = 'partial_update'
router.register(r'devices', manage.ManageViewSet, basename='fido'),
router.register(r'devices', manage.DetailViewSet, basename='fido'),


urlpatterns = [
    path('register', register.RegisterView.as_view(), name="register"),
    path('register/begin', register.begin),
    path('register/complete', register.complete),
    path('verify', verify.VerifyView.as_view()),
    path('verify/begin', verify.begin),
    path('verify/complete', verify.complete),
    path('manage/', include(router.urls)),
]
