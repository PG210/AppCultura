# Generated by Django 4.2.5 on 2023-11-30 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0018_opciones_correcta'),
    ]

    operations = [
        migrations.AddField(
            model_name='preguntas',
            name='valor',
            field=models.IntegerField(null=True),
        ),
    ]