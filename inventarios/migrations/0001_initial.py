# Generated by Django 5.1.1 on 2024-10-21 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facturacion', '0001_initial'),
        ('sucursales', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('ruc', models.CharField(max_length=13)),
                ('direccion', models.CharField(max_length=255)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_autorizacion', models.CharField(default='0000000000', max_length=50)),
                ('fecha_emision', models.DateField()),
                ('total_sin_impuestos', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_con_impuestos', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_descuento', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('metodo_pago', models.CharField(choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia')], default='efectivo', max_length=50)),
                ('estado', models.CharField(choices=[('completada', 'Completada'), ('pendiente', 'Pendiente'), ('cancelada', 'Cancelada')], default='pendiente', max_length=20)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sucursales.sucursal')),
                ('proveedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventarios.proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('unidad_medida', models.CharField(blank=True, max_length=50, null=True)),
                ('codigo_producto', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='productos/')),
                ('stock_minimo', models.IntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventarios.categoria')),
                ('impuesto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='facturacion.impuesto')),
                ('sucursales', models.ManyToManyField(blank=True, to='sucursales.sucursal')),
            ],
        ),
        migrations.CreateModel(
            name='Presentacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_presentacion', models.CharField(max_length=50)),
                ('cantidad', models.PositiveIntegerField()),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='presentaciones', to='sucursales.sucursal')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='presentaciones', to='inventarios.producto')),
            ],
        ),
        migrations.CreateModel(
            name='MovimientoInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_movimiento', models.CharField(choices=[('COMPRA', 'Compra'), ('TRANSFERENCIA_ENTRADA', 'Transferencia Entrada'), ('TRANSFERENCIA_SALIDA', 'Transferencia Salida'), ('VENTA', 'Venta')], max_length=25)),
                ('cantidad', models.IntegerField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sucursales.sucursal')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.producto')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_principal', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=255)),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_por_producto', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('impuesto_aplicado', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('valor_impuesto', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='inventarios.compra')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Transferencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.producto')),
                ('sucursal_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_entrada', to='sucursales.sucursal')),
                ('sucursal_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferencias_salida', to='sucursales.sucursal')),
            ],
        ),
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('sucursal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sucursales.sucursal')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventarios.producto')),
            ],
            options={
                'unique_together': {('producto', 'sucursal')},
            },
        ),
    ]
