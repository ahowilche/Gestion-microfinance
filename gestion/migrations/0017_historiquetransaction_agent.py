# Generated by Django 4.2.16 on 2025-06-17 01:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0016_remove_historiquetransaction_agent_credit_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='historiquetransaction',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
