# Generated by Django 5.0.4 on 2024-10-11 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_customer_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='avatar',
            field=models.ImageField(blank=True, default='/default-avatar2.png', null=True, upload_to='customers/'),
        ),
    ]
