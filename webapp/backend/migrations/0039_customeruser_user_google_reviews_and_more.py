# Generated by Django 5.1.1 on 2024-10-13 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0038_customeruser_places_reviewed"),
    ]

    operations = [
        migrations.AddField(
            model_name="customeruser",
            name="user_google_reviews",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customeruser",
            name="user_regular_reviews",
            field=models.IntegerField(default=0),
        ),
    ]