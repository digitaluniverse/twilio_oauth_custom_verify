from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("phone/verify/", views.verifyNumber.as_view(), name="verify-phone"),
    path("phone/confirm/", views.confirmPhone.as_view(), name="confirm-phone"),
    path("email/verify/", views.verifyEmail.as_view(), name="verify-email"),
    path("email/confirm/", views.confirmEmail.as_view(), name="confirm-email"),
    path("register/", views.register.as_view(), name="register"),
    path("login/", views.login.as_view(), name="login"),


]
