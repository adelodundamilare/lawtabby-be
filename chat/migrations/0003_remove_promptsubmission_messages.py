# Generated by Django 4.2.7 on 2024-04-14 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_promptsubmission_messages_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promptsubmission',
            name='messages',
        ),
    ]
