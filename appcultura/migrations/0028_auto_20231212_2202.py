# Generated by Django 3.2.22 on 2023-12-13 03:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0027_merge_20231212_0835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compromisos',
            name='con_quien',
        ),
        migrations.RemoveField(
            model_name='compromisos',
            name='id_curso',
        ),
        migrations.AddField(
            model_name='compromisos',
            name='id_sesion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.sesioncurso'),
        ),
        migrations.AddField(
            model_name='compromisos',
            name='idrespuesta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.respuestaform'),
        ),
    ]