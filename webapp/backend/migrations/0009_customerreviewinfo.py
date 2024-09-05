# Generated by Django 5.1 on 2024-09-05 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_remove_userdata_website_url_userdata_website_urls'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerReviewInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('rating', models.IntegerField()),
                ('badges', models.JSONField(blank=True, null=True)),
                ('posted_to_google_review', models.BooleanField(default=False)),
                ('generated_review_body', models.TextField(default='')),
                ('final_review_body', models.TextField(default='')),
                ('email_sent_to_company', models.BooleanField(default=False)),
            ],
        ),
    ]