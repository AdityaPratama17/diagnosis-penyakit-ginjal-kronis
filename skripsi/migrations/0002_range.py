# Generated by Django 4.0.1 on 2022-01-26 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skripsi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Range',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atribut', models.CharField(max_length=255)),
                ('max', models.CharField(max_length=255)),
                ('min', models.CharField(max_length=255)),
            ],
        ),
    ]