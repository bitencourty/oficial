# Generated by Django 5.1.2 on 2024-10-31 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomap', '0002_docente'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id_sala', models.AutoField(primary_key=True)),             # ID da sala
                ('nome_sala', models.CharField(max_length=100)),             # Nome da sala
                ('capac_sala', models.IntegerField()),                      # Capacidade da sala como IntegerField
                ('loc_sala', models.CharField(max_length=15)),              # Localização da sala
                ('status_sala', models.CharField(max_length=15)),           # Status da sala
                ('quant_equip_sala', models.IntegerField()),                # Quantidade de equipamentos como IntegerField
            ],
            options={
                'db_table': 'salas',  # Define explicitamente o nome da tabela
            },
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id_reserva', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora_inicio', models.DateTimeField()),
                ('data_hora_fim', models.DateTimeField()),
                ('status_reserva', models.CharField(max_length=15)),
                ('nome_doc', models.CharField(max_length=100)),
                ('sala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='roomap.sala')),
            ],
        ),
        migrations.DeleteModel(
            name='Reservas',
        ),
        migrations.DeleteModel(
            name='Salas',
        ),
    ]