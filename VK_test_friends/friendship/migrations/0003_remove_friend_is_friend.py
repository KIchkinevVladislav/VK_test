# Generated by Django 4.2.1 on 2023-05-08 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0002_friend_is_friend'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friend',
            name='is_friend',
        ),
    ]
