# Generated by Django 5.1.1 on 2024-10-21 18:46

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RazonSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('ruc', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator(message='El RUC debe tener exactamente 13 dígitos numéricos.', regex='^\\d{13}$')])),
            ],
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=20)),
                ('codigo_establecimiento', models.CharField(blank=True, max_length=3, null=True)),
                ('punto_emision', models.CharField(blank=True, max_length=3, null=True)),
                ('es_matriz', models.BooleanField(default=False)),
                ('secuencial_actual', models.CharField(default='000000001', max_length=9)),
                ('razon_social', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sucursales', to='sucursales.razonsocial')),
                ('usuarios', models.ManyToManyField(related_name='sucursales', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('codigo_establecimiento', 'punto_emision')},
            },
        ),
    ]
