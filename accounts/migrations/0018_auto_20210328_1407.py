# Generated by Django 3.0.7 on 2021-03-28 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_auto_20210328_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_email_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='account',
            name='is_phone_public',
            field=models.BooleanField(default=False),
        ),
    ]