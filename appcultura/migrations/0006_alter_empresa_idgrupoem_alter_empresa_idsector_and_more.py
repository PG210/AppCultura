# Generated by Django 4.2.7 on 2023-11-14 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0005_objetivoscurso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='idgrupoem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.grupoempresa'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='idsector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.sectorempresa'),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='idtam',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.tamempresa'),
        ),
        migrations.AlterField(
            model_name='empresaareas',
            name='idarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.area'),
        ),
        migrations.AlterField(
            model_name='empresaareas',
            name='idempresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appcultura.empresa'),
        ),
        migrations.AlterField(
            model_name='empresaareas',
            name='idepar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='appcultura.departamento'),
        ),
    ]
