# Generated by Django 5.1.2 on 2024-11-05 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomap', '0003_sala_reserva_delete_reservas_delete_salas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipamento',
            fields=[
                ('id_equip', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_equip', models.CharField(max_length=100)),
                ('loc_equip', models.CharField(max_length=15)),
                ('desc_equip', models.CharField(max_length=100)),
                ('status_equip', models.CharField(max_length=100)),
                ('quant_equip', models.IntegerField()),
            ],
            options={
                'db_table': 'equipamentos',
            },
        ),
    ]
