from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.base.models import generate_ulid_as_string


class User(AbstractUser):
    id = models.CharField(primary_key=True, default=generate_ulid_as_string, editable=False, max_length=26)
    email = models.EmailField(unique=True)

    class Meta:
        app_label = 'users'

    def __str__(self):
        return self.get_username()
