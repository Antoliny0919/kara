# Generated by Django 5.1.7 on 2025-03-23 00:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import kara.accounts.fields


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("bio", models.TextField(blank=True, null=True)),
                ("bio_image", models.ImageField(blank=True, null=True, upload_to="")),
                (
                    "user",
                    kara.accounts.fields.DefaultOneToOneField(
                        create=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
