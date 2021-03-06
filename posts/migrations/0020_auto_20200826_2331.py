# Generated by Django 3.0.7 on 2020-08-26 18:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import posts.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0019_auto_20200826_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grouppost',
            name='post',
        ),
        migrations.RemoveField(
            model_name='post',
            name='is_group_post',
        ),
        migrations.AddField(
            model_name='grouppost',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grouppost',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grouppost',
            name='description',
            field=models.TextField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grouppost',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=posts.models.upload_location),
        ),
        migrations.AddField(
            model_name='notification',
            name='groupPost',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.GroupPost'),
        ),
    ]
