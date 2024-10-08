# Generated by Django 4.1 on 2024-09-29 21:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sucursales", "0001_initial"),
        ("facturacion", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Categoria",
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
                ("nombre", models.CharField(max_length=200, unique=True)),
                ("descripcion", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Producto",
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
                ("nombre", models.CharField(max_length=200, unique=True)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("precio_compra", models.DecimalField(decimal_places=2, max_digits=10)),
                ("precio_venta", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "unidad_medida",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "codigo_producto",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="productos/"),
                ),
                ("stock_minimo", models.IntegerField(default=0)),
                ("activo", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "categoria",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="inventarios.categoria",
                    ),
                ),
                (
                    "impuesto",
                    models.ForeignKey(
                        default=3,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facturacion.impuesto",
                    ),
                ),
                (
                    "sucursal",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sucursales.sucursal",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Transferencia",
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
                ("fecha", models.DateTimeField(auto_now_add=True)),
                (
                    "producto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="inventarios.producto",
                    ),
                ),
                (
                    "sucursal_destino",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transferencias_entrada",
                        to="sucursales.sucursal",
                    ),
                ),
                (
                    "sucursal_origen",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transferencias_salida",
                        to="sucursales.sucursal",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MovimientoInventario",
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
                    "tipo_movimiento",
                    models.CharField(
                        choices=[
                            ("COMPRA", "Compra"),
                            ("TRANSFERENCIA_ENTRADA", "Transferencia Entrada"),
                            ("TRANSFERENCIA_SALIDA", "Transferencia Salida"),
                            ("VENTA", "Venta"),
                        ],
                        max_length=25,
                    ),
                ),
                ("cantidad", models.IntegerField()),
                ("fecha", models.DateTimeField(auto_now_add=True)),
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
            ],
        ),
        migrations.CreateModel(
            name="Compra",
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
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("fecha", models.DateTimeField(auto_now_add=True)),
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
            ],
        ),
        migrations.CreateModel(
            name="Inventario",
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
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
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
            ],
            options={
                "unique_together": {("producto", "sucursal")},
            },
        ),
    ]
