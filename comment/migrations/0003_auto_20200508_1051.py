# Generated by Django 2.0 on 2020-05-08 02:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0002_auto_20200508_0939'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='reply_on',
            new_name='reply_to',
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
    ]
