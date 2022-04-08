# Generated by Django 4.0.1 on 2022-01-26 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skripsi', '0002_range'),
    ]

    operations = [
        migrations.CreateModel(
            name='Detail_Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_rule', models.IntegerField(max_length=255)),
                ('kelas', models.CharField(max_length=255)),
                ('rule', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_rule', models.IntegerField(max_length=255)),
                ('atribut', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
    ]