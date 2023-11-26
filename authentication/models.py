from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField


# TODO table partitioning
class User(AbstractUser):
    name = "user"

    email = models.EmailField()
    username = models.CharField(blank=True, unique=True, max_length=255)
    profile_picture = models.URLField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    @classmethod
    def get_by_email(cls, email):
        return cls.objects.select_related('preference').filter(email=email).first()


class UserSession(models.Model):
    name = "user_session"

    DEVICE_TYPE_CHOICES = [
        ("APP", "app"),
        ("WEB", "web")
    ]
    session_key = models.CharField(null=False, unique=True, max_length=255)
    device_id = models.CharField(default=None, null=True, max_length=255)
    device_type = models.CharField(choices=DEVICE_TYPE_CHOICES, default="app", max_length=255)
    ip_address = models.GenericIPAddressField(default=None, null=True)
    is_active = models.BooleanField(default=True)
    expired_at = models.DateTimeField(default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "user_session"
        verbose_name_plural = "user_sessions"
        indexes = [
            models.Index("user_id", "ip_address", name="user_ip_address_idx")
        ]

    def __str__(self):
        return self.session_key


