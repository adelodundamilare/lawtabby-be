# Generated by Django 4.2.7 on 2024-04-14 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='promptsubmission',
            name='messages',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='promptsubmission',
            name='prompt',
            field=models.TextField(blank=True, null=True),
        ),
    ]
