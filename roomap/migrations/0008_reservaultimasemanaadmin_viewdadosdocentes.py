# Generated by Django 5.1.3 on 2024-11-19 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomap', '0007_salaview_viewreservasadmin'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReservaUltimaSemanaAdmin',
            fields=[
                ('id_reserva', models.IntegerField(primary_key=True, serialize=False)),
                ('nome_adm', models.CharField(max_length=100)),
                ('data_hora_inicio', models.DateTimeField()),
                ('data_hora_fim', models.DateTimeField()),
                ('status_reserva', models.CharField(max_length=15)),
                ('id_sala', models.IntegerField()),
            ],
            options={
                'db_table': 'reservas_ultima_semana_admin',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ViewDadosDocentes',
            fields=[
                ('id_docente', models.IntegerField(primary_key=True, serialize=False)),
                ('nome_doc', models.CharField(max_length=100)),
                ('email_doc', models.EmailField(max_length=100)),
                ('cargo_doc', models.CharField(max_length=100)),
                ('tel_doc', models.CharField(blank=True, max_length=100)),
                ('id_reserva', models.IntegerField(blank=True, null=True)),
                ('data_hora_inicio', models.DateTimeField(blank=True, null=True)),
                ('data_hora_fim', models.DateTimeField(blank=True, null=True)),
                ('status_reserva', models.CharField(blank=True, max_length=15, null=True)),
                ('sala_reservada', models.CharField(blank=True, max_length=100, null=True)),
                ('localizacao_sala', models.CharField(blank=True, max_length=15, null=True)),
            ],
            options={
                'db_table': 'view_dados_docentes',
                'managed': False,
            },
        ),
    ]
