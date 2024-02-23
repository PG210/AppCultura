# Generated by Django 3.2.22 on 2024-02-16 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0041_auto_20240215_1333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calificacionusuarios',
            old_name='comentario_valor_curso',
            new_name='areasmejora',
        ),
        migrations.RemoveField(
            model_name='calificacionusuarios',
            name='comentario',
        ),
        migrations.RemoveField(
            model_name='calificacionusuarios',
            name='sugerencia',
        ),
        migrations.RemoveField(
            model_name='calificacionusuarios',
            name='valoracion',
        ),
        migrations.AddField(
            model_name='calificacionusuarios',
            name='aplicabilidad',
            field=models.PositiveIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0),
        ),
        migrations.AddField(
            model_name='calificacionusuarios',
            name='claridad',
            field=models.PositiveIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0),
        ),
        migrations.AddField(
            model_name='calificacionusuarios',
            name='fortalezas',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='calificacionusuarios',
            name='relevancia',
            field=models.PositiveIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0),
        ),
        migrations.AlterField(
            model_name='calificacionusuarios',
            name='id_sesiones_curso',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.sesioncurso'),
        ),
        migrations.AlterField(
            model_name='calificacionusuarios',
            name='id_usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.userperfil'),
        ),
    ]
