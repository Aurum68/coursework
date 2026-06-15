from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


class User(AbstractUser):
    phone = PhoneNumberField(blank=True, null=True, unique=True)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=100)

    def __str__(self):
        return self.username