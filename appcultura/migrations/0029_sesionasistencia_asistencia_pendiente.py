# Generated by Django 4.2.7 on 2023-12-14 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0028_userperfil_pendiente'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesionasistencia',
            name='asistencia_pendiente',
            field=models.BooleanField(default=False, null=True),
        ),
    ]