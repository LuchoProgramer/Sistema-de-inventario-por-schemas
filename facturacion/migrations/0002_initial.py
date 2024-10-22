# Generated by Django 5.1.1 on 2024-10-21 18:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('RegistroTurnos', '0001_initial'),
        ('facturacion', '0001_initial'),
        ('inventarios', '0001_initial'),
        ('sucursales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='detallefactura',
            name='presentacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.presentacion'),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.producto'),
        ),
        migrations.AddField(
            model_name='factura',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.cliente'),
        ),
        migrations.AddField(
            model_name='factura',
            name='registroturno',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='RegistroTurnos.registroturno'),
        ),
        migrations.AddField(
            model_name='factura',
            name='sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sucursales.sucursal'),
        ),
        migrations.AddField(
            model_name='factura',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='factura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='facturacion.factura'),
        ),
        migrations.AddField(
            model_name='facturaimpuesto',
            name='factura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='impuestos', to='facturacion.factura'),
        ),
        migrations.AddField(
            model_name='facturaimpuesto',
            name='impuesto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facturacion.impuesto'),
        ),
        migrations.AddField(
            model_name='pago',
            name='factura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='facturacion.factura'),
        ),
        migrations.AlterUniqueTogether(
            name='factura',
            unique_together={('sucursal', 'numero_autorizacion')},
        ),
    ]
