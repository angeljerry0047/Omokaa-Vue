# Generated by Django 3.0.7 on 2020-10-10 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='filename',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='is_file',
            field=models.BooleanField(default=False),
        ),
    ]
