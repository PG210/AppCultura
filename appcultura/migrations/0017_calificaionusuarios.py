# Generated by Django 4.2.7 on 2023-11-30 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0016_sesionasistencia'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalificaionUsuarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField()),
                ('valoracion', models.PositiveIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('sugerencia', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('estado', models.BooleanField(default=True)),
                ('id_sesiones_curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.sesioncurso')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.userperfil')),
            ],
        ),
    ]
