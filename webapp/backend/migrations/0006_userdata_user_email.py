# Generated by Django 5.1 on 2024-09-02 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0005_userdata_website_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdata",
            name="user_email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
