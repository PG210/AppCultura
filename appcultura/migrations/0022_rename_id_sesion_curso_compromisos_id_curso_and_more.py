# Generated by Django 4.2.7 on 2023-12-06 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0021_compromisos_estadocompromisos_personascompromisos_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compromisos',
            old_name='id_sesion_curso',
            new_name='id_curso',
        ),
        migrations.AlterField(
            model_name='compromisos',
            name='puntaje',
            field=models.IntegerField(default=0),
        ),
    ]