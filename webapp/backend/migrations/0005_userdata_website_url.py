# Generated by Django 5.1 on 2024-09-02 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_userdata_worry_dialog_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='website_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
