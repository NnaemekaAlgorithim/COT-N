from contextvars import ContextVar

from django.conf import settings
from django.db import models
from ulid import ULID

_current_user: ContextVar = ContextVar('current_user', default=None)


def generate_ulid_as_string():
    return str(ULID())


def get_current_user():
    return _current_user.get()


def set_current_user(user):
    _current_user.set(user)


def clear_current_user():
    _current_user.set(None)


class BaseModel(models.Model):
    id = models.CharField(primary_key=True, default=generate_ulid_as_string, editable=False, max_length=26)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_%(class)s',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='updated_%(class)s',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk and user is not None:
            self.created_by = user
        if user is not None:
            self.updated_by = user
        super().save(*args, **kwargs)


class BaseAuditModel(BaseModel):
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'base'
        abstract = True
