# Generated by Django 4.1 on 2024-09-07 05:59

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facturacion", "0010_remove_impuesto_monto_impuesto_activo"),
    ]

    operations = [
        migrations.AddField(
            model_name="factura",
            name="valor_iva",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=10
            ),
        ),
    ]