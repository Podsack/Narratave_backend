from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    name = "user"

    ROLE_CHOICES = [
        ("CONSUMER", "consumer"),
        ("ARTIST", "artist"),
        ("AUTHOR", "author")
    ]

    email = models.EmailField()
    username = None
    role = models.CharField(choices=ROLE_CHOICES, default="CONSUMER", max_length=255)
    profile_picture = models.URLField(blank=True,null=True)
    dob = models.DateField(null=True, blank=True)
    country = models.CharField(blank=True, max_length=255)
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ['email']
    verbose_name = "user"

    def clean(self):
        super().clean()

        existing_users = User.objects.filter(email=self.email, role=self.role)
        if existing_users.exists() and self.pk != existing_users.first().pk:
            raise ValidationError('Email must be unique per role.')

    def __str__(self):
        return self.email

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'role'], name='unique_email_per_role')
        ]


class UserSession(models.Model):
    name = "user_sessions"
    verbose_name = "user_sessions"

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

    def __str__(self):
        return self.session_key
