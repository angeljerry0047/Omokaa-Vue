# Generated by Django 3.0.7 on 2020-10-03 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0034_auto_20200917_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(choices=[('postlike', 'postlike'), ('postdislike', 'postdislike'), ('commentdislike', 'commentdislike'), ('commentlike', 'commentlike'), ('postcomment', 'postcomment'), ('commentreply', 'commentreply'), ('rating', 'rating')], max_length=100),
        ),
    ]