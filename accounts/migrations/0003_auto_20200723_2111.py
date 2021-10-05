# Generated by Django 3.0.7 on 2020-07-23 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='date_birth',
            field=models.DateTimeField(null=True, verbose_name='Date of birth'),
        ),
        migrations.AddField(
            model_name='account',
            name='identity',
            field=models.CharField(max_length=255, null=True, verbose_name='identity'),
        ),
        migrations.AddField(
            model_name='account',
            name='user_type',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ExtendAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.IntegerField(blank=True, null=True)),
                ('date_birth', models.DateTimeField(verbose_name='Date of birth')),
                ('identity', models.CharField(max_length=255, verbose_name='identity')),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='')),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
