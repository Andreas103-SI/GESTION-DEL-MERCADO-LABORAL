# Generated by Django 4.2.20 on 2025-04-15 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market_analysis', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='joboffer',
            old_name='rl',
            new_name='url',
        ),
    ]
