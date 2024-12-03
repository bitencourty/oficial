# Generated by Django 5.1.2 on 2024-11-26 16:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roomap', '0010_reservadiaatualadmin_delete_viewreservasadmin_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id_turno', models.AutoField(primary_key=True, serialize=False)),
                ('nome_turno', models.CharField(max_length=50)),
                ('horario_inicio', models.TimeField()),
                ('horario_fim', models.TimeField()),
            ],
            options={
                'db_table': 'turnos',
            },
        ),
        migrations.AddField(
            model_name='reservaadm',
            name='turno',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='roomap.turno'),
            preserve_default=False,
        ),
    ]
