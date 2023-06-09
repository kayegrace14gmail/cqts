# Generated by Django 4.2.1 on 2023-06-29 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_batch_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='color',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='batch',
            name='cooperative',
            field=models.ForeignKey(blank=True, limit_choices_to={'group__name': 'Cooperative'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cooperative_batches', to=settings.AUTH_USER_MODEL),
        ),
    ]
