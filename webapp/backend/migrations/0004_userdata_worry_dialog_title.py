# Generated by Django 5.1 on 2024-09-02 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_userdata_worry_dialog_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='worry_dialog_title',
            field=models.TextField(blank=True, null=True),
        ),
    ]
