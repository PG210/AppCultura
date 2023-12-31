# Generated by Django 4.2.7 on 2023-12-05 15:59

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0020_merge_20231204_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compromisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compromiso', models.TextField()),
                ('prioridad', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='La prioridad no puede ser inferior a 1'), django.core.validators.MaxValueValidator(3, message='La prioridad no puede ser mayor a 3')])),
                ('fecha_compromiso', models.DateField(auto_now=True)),
                ('fecha_final', models.DateField()),
                ('puntaje', models.IntegerField()),
                ('estado', models.BooleanField(default=True)),
                ('con_quien', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.userperfil')),
            ],
        ),
        migrations.CreateModel(
            name='EstadoCompromisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PersonasCompromisos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_compromiso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.compromisos')),
                ('id_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.userperfil')),
            ],
        ),
        migrations.AddField(
            model_name='compromisos',
            name='id_estado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.estadocompromisos'),
        ),
        migrations.AddField(
            model_name='compromisos',
            name='id_sesion_curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.sesioncurso'),
        ),
    ]
