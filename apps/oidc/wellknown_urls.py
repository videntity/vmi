from django.urls import path

from . import views

urlpatterns = [
    path('openid-configuration', views.Wellknown.as_view()),
    path('certs', views.JWKSURI.as_view(), name="jwks_uri"),
]
