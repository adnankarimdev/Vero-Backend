# Generated by Django 5.1 on 2024-09-10 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0021_reviewstopostlater_posted_to_google'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewstopostlater',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]