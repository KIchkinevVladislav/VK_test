# Generated by Django 4.2.1 on 2023-05-08 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0003_remove_friend_is_friend'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('D', 'Declined')], default='P', max_length=1),
        ),
    ]