from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers

# Create your models here.
class CustomUser(AbstractUser):
    number = PhoneNumberField(
        null=True,
        blank=True,
        unique=True,
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]


    def get_number(self):
        try:
            parsed = phonenumbers.parse(str(self.number), None)
        except phonenumbers.NumberParseException:
            return None
        return parsed

    def __str__(self):
        return self.email