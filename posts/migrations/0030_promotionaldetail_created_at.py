# Generated by Django 3.0.7 on 2020-09-03 15:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0029_auto_20200903_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionaldetail',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
