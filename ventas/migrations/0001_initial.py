# Generated by Django 4.1 on 2024-09-29 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sucursales", "0001_initial"),
        ("RegistroTurnos", "0001_initial"),
        ("facturacion", "0002_initial"),
        ("inventarios", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Venta",
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
                ("cantidad", models.IntegerField()),
                (
                    "precio_unitario",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "total_venta",
                    models.DecimalField(
                        decimal_places=2, editable=False, max_digits=10
                    ),
                ),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                (
                    "metodo_pago",
                    models.CharField(
                        choices=[
                            ("01", "Sin utilización del sistema financiero"),
                            ("15", "Compensación de deudas"),
                            ("16", "Tarjeta de débito"),
                            ("17", "Dinero electrónico"),
                            ("18", "Tarjeta prepago"),
                            ("19", "Tarjeta de crédito"),
                            ("20", "Otros con utilización del sistema financiero"),
                            ("21", "Endoso de títulos"),
                        ],
                        default="01",
                        help_text="Método de pago utilizado para la venta",
                        max_length=2,
                    ),
                ),
                (
                    "factura",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ventas",
                        to="facturacion.factura",
                    ),
                ),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventarios.producto",
                    ),
                ),
                (
                    "sucursal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sucursales.sucursal",
                    ),
                ),
                (
                    "turno",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ventas",
                        to="RegistroTurnos.registroturno",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CierreCaja",
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
                (
                    "efectivo_total",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("tarjeta_total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "transferencia_total",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "salidas_caja",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ("fecha_cierre", models.DateTimeField(auto_now_add=True)),
                (
                    "sucursal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sucursales.sucursal",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Carrito",
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
                ("cantidad", models.PositiveIntegerField(default=1)),
                ("agregado_el", models.DateTimeField(auto_now_add=True)),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventarios.producto",
                    ),
                ),
                (
                    "turno",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="carritos",
                        to="RegistroTurnos.registroturno",
                    ),
                ),
            ],
        ),
    ]
