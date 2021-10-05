# Generated by Django 3.0.7 on 2020-11-09 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0037_auto_20201101_1551'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buyproposals',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='sellproposals',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='workproposal',
            options={'ordering': ['id']},
        ),
        migrations.RenameField(
            model_name='hirecomment',
            old_name='user',
            new_name='bidder',
        ),
        migrations.RenameField(
            model_name='hirecomment',
            old_name='message',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='workproposal',
            old_name='user',
            new_name='bidder',
        ),
        migrations.AddField(
            model_name='buyproposals',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.BuyProposals'),
        ),
        migrations.AddField(
            model_name='sellproposals',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.SellProposals'),
        ),
        migrations.AddField(
            model_name='workproposal',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.WorkProposal'),
        ),
        migrations.AlterField(
            model_name='buyproposals',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='sellproposals',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='workproposal',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='documents/'),
        ),
    ]