# Generated by Django 5.1.2 on 2024-11-07 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomap', '0004_equipamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docente',
            name='id_doc',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='equipamento',
            name='id_equip',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='id_reserva',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sala',
            name='id_sala',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterModelTable(
            name='docente',
            table='docentes',
        ),
    ]