# Generated by Django 3.0.7 on 2021-02-18 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_account_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='country_code',
            field=models.CharField(max_length=5, null=True, verbose_name='country_code'),
        ),
    ]