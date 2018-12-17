from django.urls import path

urlpatterns = [
    path('register/begin', views.register.begin),
    path('register/complete', views.register.complete),
    path('authenticate/begin', views.authenticate.begin),
    path('authenticate/complete', views.authenticate.complete),
]
