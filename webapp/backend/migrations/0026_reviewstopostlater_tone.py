# Generated by Django 5.1 on 2024-09-16 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0025_userdata_email_delay"),
    ]

    operations = [
        migrations.AddField(
            model_name="reviewstopostlater",
            name="tone",
            field=models.CharField(default="", max_length=255),
        ),
    ]
