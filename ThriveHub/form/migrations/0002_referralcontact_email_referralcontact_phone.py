# Generated by Django 5.1.2 on 2024-12-13 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='referralcontact',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='referralcontact',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
