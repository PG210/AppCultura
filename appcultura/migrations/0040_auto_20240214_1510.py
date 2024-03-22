# Generated by Django 3.2.22 on 2024-02-14 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0039_formadorempresa_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='curso',
            name='idempresa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.empresa'),
        ),
        migrations.AddField(
            model_name='curso',
            name='idusu',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.userperfil'),
        ),
    ]