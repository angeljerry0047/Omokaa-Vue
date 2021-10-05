# Generated by Django 3.0.7 on 2021-03-28 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_account_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='audience',
        ),
        migrations.AddField(
            model_name='account',
            name='explore_locations',
            field=models.CharField(max_length=5, null=True, verbose_name='explore_locations'),
        ),
    ]
