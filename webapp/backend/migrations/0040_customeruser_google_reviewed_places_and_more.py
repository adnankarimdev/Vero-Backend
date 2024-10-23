# Generated by Django 5.1.1 on 2024-10-13 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0039_customeruser_user_google_reviews_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customeruser",
            name="google_reviewed_places",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="customeruser",
            name="place_review_dates",
            field=models.JSONField(default=dict),
        ),
    ]