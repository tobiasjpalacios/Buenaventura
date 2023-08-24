# Generated by Django 3.1.2 on 2023-05-30 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BAapp', '0010_auto_20230530_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='categoria_iva',
            field=models.CharField(blank=True, choices=[('RIM', 'Responsable Inscripto M'), ('CF', 'Consumidor Final'), ('EX', 'Exento'), ('RI', 'Responsable Inscripto'), ('MO', 'Monotributo')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='negocio',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
