# Generated by Django 2.0.5 on 2019-04-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostlock', '0003_auto_20190423_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='host',
            name='lock_state',
        ),
        migrations.AddField(
            model_name='host',
            name='is_locked',
            field=models.BooleanField(default=False, help_text='select if this host is currently locked'),
        ),
    ]
