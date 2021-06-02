from django.db.models.fields import CharField
from rest_framework import serializers
from . import models
from django.contrib.auth.hashers import make_password
from oauth2_provider.models import get_access_token_model, get_application_model, get_refresh_token_model
import phonenumbers
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.exceptions import ValidationError
from oauthlib import common
from django.utils import timezone
from datetime import datetime, timedelta
from oauth2_provider.settings import oauth2_settings
from .verify import verifications, verification_checks
from rest_framework.fields import CharField


class RegisterSerializer(serializers.Serializer):
    email = CharField(min_length=4)
    password = CharField(min_length=4)

    def validate(self, data):
        queryset = models.CustomUser.objects.all()
        try:
            email = data.get('email')
            queryset.get(username=email)
            raise serializers.ValidationError({"Error": "Email Already Exists"})
        except models.CustomUser.DoesNotExist:
            pass
        if not data.get('email'):
            raise serializers.ValidationError(
                {"Error": "Email can not be empty"})
        if not data.get('password'):
            raise serializers.ValidationError(
                {"Error": "Password can not be empty"})
        try:
            verifications(email, 'email')
        except Exception as error:
            raise serializers.ValidationError({"Error": str(error)})
        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CustomUser
        fields = ['id','email','number','phone_verified','email_verified']


