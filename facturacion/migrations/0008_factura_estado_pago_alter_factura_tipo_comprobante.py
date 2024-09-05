# Generated by Django 4.1 on 2024-09-05 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facturacion", "0007_impuesto_codigo_impuesto"),
    ]

    operations = [
        migrations.AddField(
            model_name="factura",
            name="estado_pago",
            field=models.CharField(
                choices=[
                    ("PENDIENTE", "Pendiente"),
                    ("PAGADO_PARCIAL", "Pagado Parcialmente"),
                    ("PAGADO", "Pagado"),
                ],
                default="PENDIENTE",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="factura",
            name="tipo_comprobante",
            field=models.CharField(
                choices=[
                    ("01", "Factura"),
                    ("03", "Liquidación de compra de bienes y prestación de servicios"),
                    ("04", "Nota de crédito"),
                    ("05", "Nota de débito"),
                    ("06", "Guía de remisión"),
                    ("07", "Comprobante de retención"),
                ],
                default="01",
                max_length=2,
            ),
        ),
    ]
