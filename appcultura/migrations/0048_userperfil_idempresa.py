# Generated by Django 3.2.22 on 2024-06-25 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0047_grupos_idempresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='userperfil',
            name='idempresa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.empresa'),
        ),
    ]
