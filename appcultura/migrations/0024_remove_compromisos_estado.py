# Generated by Django 4.2.7 on 2023-12-06 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0023_alter_compromisos_estado_alter_compromisos_id_curso_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compromisos',
            name='estado',
        ),
    ]