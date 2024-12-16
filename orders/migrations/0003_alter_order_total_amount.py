# Generated by Django 4.2 on 2024-12-16 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]