# Generated by Django 4.2.1 on 2023-05-26 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_farmer_options_alter_batch_buyer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]