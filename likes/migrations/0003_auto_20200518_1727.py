# Generated by Django 2.0 on 2020-05-18 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('likes', '0002_auto_20200516_2255'),
    ]

    operations = [
        migrations.RenameField(
            model_name='likerecord',
            old_name='liked_num',
            new_name='liked_time',
        ),
        migrations.AlterField(
            model_name='likerecord',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
