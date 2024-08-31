# Generated by Django 4.1 on 2024-08-30 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sucursales", "0002_sucursal_codigo_establecimiento_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sucursal",
            name="codigo_establecimiento",
            field=models.CharField(blank=True, max_length=3, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="sucursal",
            name="nombre",
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name="sucursal",
            name="punto_emision",
            field=models.CharField(blank=True, max_length=3, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="sucursal",
            name="razon_social",
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name="sucursal",
            name="ruc",
            field=models.CharField(blank=True, max_length=13, null=True, unique=True),
        ),
    ]
