# Generated by Django 4.0.1 on 2022-02-25 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skripsi', '0006_range_diskrit'),
    ]

    operations = [
        migrations.CreateModel(
            name='KFCV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_data', models.IntegerField()),
                ('fold', models.IntegerField()),
            ],
        ),
    ]
