# Generated by Django 4.1 on 2024-09-29 21:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("inventarios", "0001_initial"),
        ("sucursales", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ConteoDiario",
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
                ("fecha_conteo", models.DateField(auto_now_add=True)),
                ("cantidad_contada", models.IntegerField()),
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
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]