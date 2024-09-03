# Generated by Django 4.1 on 2024-09-02 23:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sucursales", "0003_alter_sucursal_codigo_establecimiento_and_more"),
        ("empleados", "0004_registroturno"),
        ("facturacion", "0002_cotizacion"),
    ]

    operations = [
        migrations.CreateModel(
            name="ComprobantePago",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cliente", models.CharField(blank=True, max_length=200, null=True)),
                ("fecha_emision", models.DateTimeField(auto_now_add=True)),
                (
                    "numero_autorizacion",
                    models.CharField(blank=True, max_length=49, null=True, unique=True),
                ),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("observaciones", models.TextField(blank=True, null=True)),
                (
                    "empleado",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="empleados.empleado",
                    ),
                ),
                (
                    "sucursal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sucursales.sucursal",
                    ),
                ),
            ],
        ),
    ]
