# Generated by Django 5.1.1 on 2024-10-21 20:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_initial'),
        ('sucursales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='razon_social',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sucursales.razonsocial'),
        ),
    ]
