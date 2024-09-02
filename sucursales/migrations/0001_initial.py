# Generated by Django 4.1 on 2024-08-22 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Sucursal",
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
                ("direccion", models.TextField()),
                ("telefono", models.CharField(max_length=20)),
                ("es_matriz", models.BooleanField(default=False)),
            ],
        ),
    ]