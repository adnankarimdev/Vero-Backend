from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class CustomerReviewInfo(models.Model):
    location = models.CharField(max_length=255)  # Required string
    place_id_from_review = models.CharField(max_length=255, default='')
    rating = models.IntegerField()  # Required number
    badges = models.JSONField(blank=True, null=True)  # Optional array of strings
    posted_to_google_review = models.BooleanField(default=False)  # Defaults to false
    generated_review_body = models.TextField(default='')  # Defaults to empty string
    final_review_body = models.TextField(default='')  # Defaults string
    email_sent_to_company = models.BooleanField(default=False)  # Defaults to false
    analyzed_review_details = models.JSONField(blank=True, null=True) 
    time_taken_to_write_review_in_seconds = models.FloatField(blank=True, null=True)
    review_date = models.CharField(max_length=255, default='')

    def __str__(self):
        return f"{self.location} - {self.rating}"
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
    website_urls = models.TextField(blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)

    def set_place_ids(self, place_ids_list):
        self.place_ids = json.dumps(place_ids_list)

    def get_place_ids(self):
        if self.place_ids:
            return json.loads(self.place_ids)
        return []
    def __str__(self):
        return f"Data for {self.client_email}"