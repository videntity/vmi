from django.urls import path
from .views import (
    register,
    authenticate,
)

urlpatterns = [
    path('register', register.RegisterView.as_view()),
    path('register/begin', register.begin),
    path('register/complete', register.complete),
    path('authenticate/begin', authenticate.begin),
    path('authenticate/complete', authenticate.complete),
]
