# Generated by Django 4.2.16 on 2025-06-17 00:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0013_alter_client_agent_alter_compte_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='historiquetransaction',
            name='agent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='compte',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comptes', to='gestion.client'),
        ),
    ]
