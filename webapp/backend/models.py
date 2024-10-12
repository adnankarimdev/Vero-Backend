from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import json


class CustomerReviewInfo(models.Model):
    location = models.CharField(max_length=255)  # Required string
    place_id_from_review = models.CharField(max_length=255, default="")
    rating = models.IntegerField()  # Required number
    badges = models.JSONField(blank=True, null=True)  # Optional array of strings
    posted_to_google_review = models.BooleanField(default=False)  # Defaults to false
    generated_review_body = models.TextField(default="")  # Defaults to empty string
    final_review_body = models.TextField(default="")  # Defaults string
    email_sent_to_company = models.BooleanField(default=False)  # Defaults to false
    text_sent_for_review = models.BooleanField(default=False)
    analyzed_review_details = models.JSONField(blank=True, null=True)
    time_taken_to_write_review_in_seconds = models.FloatField(blank=True, null=True)
    review_date = models.CharField(max_length=255, default="")
    posted_with_bubble_rating_platform = models.BooleanField(default=False)
    posted_with_in_store_mode = models.BooleanField(default=False)
    review_uuid = models.CharField(max_length=255, default="")
    posted_to_google_after_email_sent = models.BooleanField(default=False)
    pending_google_review = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.location} - {self.rating}"


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    business_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=100, default="google-business")
    account_subscription = models.CharField(max_length=100, default="free-trial")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "business_name"]

    def __str__(self):
        return self.email


class CustomerUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    user_score = models.IntegerField(default=0)
    user_reviews = models.JSONField(blank=True, null=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username", "email"]
    groups = models.ManyToManyField(
        Group, related_name="customeruser_groups", blank=True  # Different related_name
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customeruser_permissions",  # Different related_name
        blank=True,
    )

    def __str__(self):
        return self.email


class ReviewsToPostLater(models.Model):
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    google_review_url = models.TextField(blank=True, null=True)
    review_uuid = models.CharField(max_length=255, default="")
    review_body = models.TextField(blank=True, null=True)
    customer_url = models.TextField(blank=True, null=True)
    posted_to_google = models.BooleanField(default=False)
    tone = models.CharField(max_length=255, default="")
    badges = models.JSONField(blank=True, null=True)  # Optional array of strings

    def __str__(self):
        return self.email


class UserData(models.Model):
    email_intro = models.TextField(blank=True, null=True)
    email_signature = models.TextField(blank=True, null=True)
    email_body = models.TextField(blank=True, null=True)
    email_app_password = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    worry_rating = models.IntegerField(default=4)
    show_worry_dialog = models.BooleanField(default=True)
    place_ids = models.TextField(blank=True, null=True)
    show_complimentary_item = models.BooleanField(default=False)
    complimentary_item = models.CharField(max_length=255, blank=True, null=True)
    worry_dialog_body = models.TextField(blank=True, null=True)
    worry_dialog_title = models.TextField(blank=True, null=True)
    categories = models.JSONField(blank=True, null=True)
    places_information = models.JSONField(blank=True, null=True)
    website_urls = models.TextField(blank=True, null=True)
    in_location_urls = models.TextField(blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)
    company_website_urls = models.JSONField(blank=True, null=True)
    company_keywords = models.JSONField(blank=True, null=True)
    bubble_rating_platform = models.BooleanField(default=True)
    email_delay = models.IntegerField(default=60)
    card_description = models.CharField(blank=True, default="How did we do? 🤔")

    def set_place_ids(self, place_ids_list):
        self.place_ids = json.dumps(place_ids_list)

    def get_place_ids(self):
        if self.place_ids:
            return json.loads(self.place_ids)
        return []

    def __str__(self):
        return f"Data for {self.client_email}"


class ScheduledJob(models.Model):
    job_id = models.CharField(max_length=100, unique=True)
    run_date = models.DateTimeField()
    args = models.JSONField()  # Store args as JSON
    job_name = models.CharField(max_length=200)

    def __str__(self):
        return self.job_name
