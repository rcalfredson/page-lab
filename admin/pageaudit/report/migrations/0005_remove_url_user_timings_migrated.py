# Generated by Django 2.0.8 on 2018-11-02 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0004_url_user_timings_migrated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='url',
            name='user_timings_migrated',
        ),
    ]