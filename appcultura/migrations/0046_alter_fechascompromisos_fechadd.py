# Generated by Django 3.2.22 on 2024-03-21 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0045_fechascompromisos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fechascompromisos',
            name='fechadd',
            field=models.DateField(),
        ),
    ]
