# Generated by Django 4.2.5 on 2023-11-29 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0016_sesionasistencia'),
    ]

    operations = [
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('descrip', models.TextField(null=True)),
                ('estado', models.BooleanField(default=True)),
                ('fecha', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Preguntas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descrip', models.TextField(null=True)),
                ('tipo', models.CharField(max_length=255)),
                ('estado', models.BooleanField(default=True)),
                ('idform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.formulario')),
            ],
        ),
        migrations.CreateModel(
            name='Opciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descrip', models.TextField(null=True)),
                ('idpreg', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.preguntas')),
            ],
        ),
    ]
