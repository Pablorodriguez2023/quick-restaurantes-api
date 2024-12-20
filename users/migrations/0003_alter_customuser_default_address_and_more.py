# Generated by Django 4.2 on 2024-12-16 21:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("restaurants", "0002_restaurant_owner"),
        ("users", "0002_customuser_hashed_address_customuser_hashed_phone_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="default_address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="first_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="phone",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="restaurant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="restaurants.restaurant",
            ),
        ),
    ]
