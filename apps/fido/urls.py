from django.urls import path
from .views import (
    register,
    verify,
)

urlpatterns = [
    path('register', register.RegisterView.as_view(), name="register"),
    path('register/begin', register.begin),
    path('register/complete', register.complete),
    path('verify', verify.VerifyView.as_view()),
    path('verify/begin', verify.begin),
    path('verify/complete', verify.complete),
]
