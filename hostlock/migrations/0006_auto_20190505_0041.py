# Generated by Django 2.0.5 on 2019-05-05 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostlock', '0005_auto_20190429_0118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lock',
            name='expiration',
        ),
        migrations.AddField(
            model_name='lock',
            name='expires_at',
            field=models.DateTimeField(blank=True, help_text='date/time when this lock expires', null=True),
        ),
    ]
