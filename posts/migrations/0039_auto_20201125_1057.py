# Generated by Django 3.0.7 on 2020-11-25 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0038_auto_20201109_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='detail',
            field=models.TextField(max_length=800),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=800, null=True, unique_for_date='date_published'),
        ),
    ]
