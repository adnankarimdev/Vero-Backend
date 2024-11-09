# Generated by Django 5.1.1 on 2024-11-05 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0046_userdata_customer_website_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebsiteDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("website_key", models.TextField(blank=True, null=True)),
                ("website_details", models.JSONField(blank=True, null=True)),
            ],
        ),
    ]