# Generated by Django 2.0.5 on 2019-05-22 00:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('_common', '0002_auto_20190521_1555'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpreferences',
            name='favorites',
        ),
        migrations.RemoveField(
            model_name='userpreferences',
            name='recents',
        ),
        migrations.AddField(
            model_name='userfavorite',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userrecent',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='userfavorite',
            unique_together={('url', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='userrecent',
            unique_together={('url', 'user')},
        ),
    ]