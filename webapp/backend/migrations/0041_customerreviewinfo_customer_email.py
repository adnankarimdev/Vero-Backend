# Generated by Django 5.1.1 on 2024-10-14 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0040_customeruser_google_reviewed_places_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerreviewinfo",
            name="customer_email",
            field=models.CharField(default="", max_length=255),
        ),
    ]
