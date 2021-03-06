# Generated by Django 3.0.7 on 2020-09-03 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0028_auto_20200831_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_promotional',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='PromotionalDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package_type', models.CharField(choices=[('1000', '1000'), ('3000', '3000')], max_length=20)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Post')),
            ],
        ),
    ]
