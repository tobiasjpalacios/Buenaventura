# Generated by Django 3.1.2 on 2021-08-22 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BAapp', '0002_auto_20210822_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='categoria_iva',
            field=models.CharField(blank=True, choices=[('EX', 'Exento'), ('CF', 'Consumidor Final'), ('MO', 'Monotributo'), ('RI', 'Responsable Inscripto'), ('RIM', 'Responsable Inscripto M')], max_length=25, null=True),
        ),
    ]