from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    business_name = models.CharField(max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'business_name']

    def __str__(self):
        return self.email


class UserData(models.Model):
    email_intro = models.TextField(blank=True, null=True)
    email_signature = models.TextField(blank=True, null=True)
    email_body = models.TextField(blank=True, null=True)
    email_app_password = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    worry_rating = models.IntegerField(default=3)
    show_worry_dialog = models.BooleanField(default=True)
    place_ids = models.TextField(blank=True, null=True)
    show_complimentary_item = models.BooleanField(default=False)
    complimentary_item = models.CharField(max_length=255, blank=True, null=True)
    worry_dialog_body = models.TextField(blank=True, null=True)
    worry_dialog_title = models.TextField(blank=True, null=True)
    # Assuming you want to link questions to this model
    questions = models.JSONField(blank=True, null=True)  # or use a separate model

    def __str__(self):
        return f"Data for {self.client_email}"