from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, identifier, email, password=None, **extra_fields):
        if not identifier: raise ValueError('Identifier is required')
        if not email: raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(identifier=identifier, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifier, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(identifier, email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None 
    identifier = models.CharField(max_length=20, unique=True, verbose_name="Adm/Employee Number")
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'identifier' # Users log in with this
    REQUIRED_FIELDS = ['email']   # Required for createsuperuser

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.identifier} ({self.email})"