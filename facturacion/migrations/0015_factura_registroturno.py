# Generated by Django 4.1 on 2024-09-12 05:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("empleados", "0007_remove_registroturno_facturas"),
        ("facturacion", "0014_alter_factura_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="factura",
            name="registroturno",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="empleados.registroturno",
            ),
        ),
    ]