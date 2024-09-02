from django.contrib.auth.models import AbstractUser
from django.db import models
import json
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
    questions = models.JSONField(blank=True, null=True) 
    places_information = models.JSONField(blank=True, null=True) 
    website_url = models.URLField(blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)

    def set_place_ids(self, place_ids_list):
        self.place_ids = json.dumps(place_ids_list)

    def get_place_ids(self):
        if self.place_ids:
            return json.loads(self.place_ids)
        return []
    def __str__(self):
        return f"Data for {self.client_email}"