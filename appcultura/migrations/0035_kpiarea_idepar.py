# Generated by Django 3.2.22 on 2024-02-08 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0034_auto_20240206_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='kpiarea',
            name='idepar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.departamento'),
        ),
    ]