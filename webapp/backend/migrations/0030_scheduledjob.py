# Generated by Django 5.1.1 on 2024-09-29 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0029_reviewstopostlater_badges"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScheduledJob",
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
                ("job_id", models.CharField(max_length=100, unique=True)),
                ("run_date", models.DateTimeField()),
                ("args", models.JSONField()),
                ("job_name", models.CharField(max_length=200)),
            ],
        ),
    ]
