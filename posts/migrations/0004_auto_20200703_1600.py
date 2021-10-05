# Generated by Django 3.0.7 on 2020-07-03 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20200703_1553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='type',
        ),
        migrations.AddField(
            model_name='category',
            name='type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='posts.Type'),
            preserve_default=False,
        ),
    ]