# Generated by Django 4.2.1 on 2023-07-04 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_batch_color_alter_batch_cooperative'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='batch_string',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]