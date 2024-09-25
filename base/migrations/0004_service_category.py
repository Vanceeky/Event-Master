# Generated by Django 5.0.4 on 2024-09-15 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_servicepost_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.CharField(blank=True, choices=[('Photographer', 'Photographer'), ('Videographer', 'Videographer'), ('Catering', 'Catering'), ('Venue Rental', 'Venue Rental'), ('Master of Ceremony', 'Master of Ceremony')], max_length=255, null=True),
        ),
    ]
