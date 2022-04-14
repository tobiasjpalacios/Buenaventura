# Generated by Django 3.1.2 on 2021-02-09 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('BAapp', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            ('CREATE FULLTEXT INDEX BAapp_articulo_fulltext_index ON BAapp_articulo (marca, ingrediente, concentracion)',),
            ('DROP INDEX BAapp_articulo_fulltext_index ON BAapp_articulo')
        )
    ]