# Generated by Django 3.0.7 on 2020-08-31 04:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0026_auto_20200831_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='detail',
            field=models.TextField(validators=[django.core.validators.MaxLengthValidator(1000)]),
        ),
    ]
