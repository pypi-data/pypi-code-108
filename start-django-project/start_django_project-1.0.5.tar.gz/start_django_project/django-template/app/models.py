from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomAccountManager(BaseUserManager):
    # This class let us define our own custom sign up and sign in methods.

    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

        pass

class MyUser(AbstractBaseUser, PermissionsMixin):
    # Note: You can'T call the model User as this is a built-in model.
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)

    is_staff = models.BooleanField(_('staff'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    # This tells django to use the email as the main sign in field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        "username"
    ]

    objects = CustomAccountManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')