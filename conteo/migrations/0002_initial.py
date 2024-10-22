# Generated by Django 5.1.1 on 2024-10-21 18:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('conteo', '0001_initial'),
        ('inventarios', '0001_initial'),
        ('sucursales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='conteodiario',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.producto'),
        ),
        migrations.AddField(
            model_name='conteodiario',
            name='sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sucursales.sucursal'),
        ),
        migrations.AddField(
            model_name='conteodiario',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]