# Generated by Django 5.0.4 on 2024-09-17 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_event_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='budget',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
