# Generated by Django 5.1 on 2024-09-06 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0012_customerreviewinfo_time_taken_to_write_review_in_seconds"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerreviewinfo",
            name="review_date",
            field=models.CharField(default="", max_length=255),
        ),
    ]
