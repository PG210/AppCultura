# Generated by Django 3.2.22 on 2023-11-21 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcultura', '0011_merge_20231117_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('descrip', models.TextField(null=True)),
            ],
        ),
    ]
