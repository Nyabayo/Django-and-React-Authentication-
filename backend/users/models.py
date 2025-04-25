from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django_otp.plugins.otp_email.models import EmailDevice
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier,
    integrated with Role-Based Access Control (RBAC),
    and Two-Factor Authentication (2FA) support.
    """

    class Role(models.TextChoices):
        SEEKER = 'seeker', _('House Seeker')
        OWNER = 'owner', _('Property Owner')
        MANAGER = 'manager', _('Property Manager')
        ADMIN = 'admin', _('Administrator')

    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    email = models.EmailField(_("Email Address"), max_length=254, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    # ✅ NEW: Tracks whether user has completed OTP verification after login
    is_otp_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    # ✅ Role field for RBAC support
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SEEKER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class UserOTPDevice(models.Model):
    """
    Associates a user with their OTP email device.
    Used for Two-Factor Authentication (2FA).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp_device')
    email_device = models.OneToOneField(EmailDevice, on_delete=models.CASCADE, related_name='user_otp_ref')

    def __str__(self):
        return f"{self.user.email} - OTP Device"
