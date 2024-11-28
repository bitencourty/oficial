from django.db import models


class Sala(models.Model):
    id_sala = models.IntegerField(primary_key=True)
    nome_sala = models.CharField(max_length=100)
    capac_sala = models.IntegerField()
    loc_sala = models.CharField(max_length=15)
    status_sala = models.CharField(max_length=15)
    quant_equip_sala = models.IntegerField()

    class Meta:
        db_table = 'salas'

    def __str__(self):
        return self.nome_sala

class Reserva(models.Model):
    id_reserva = models.IntegerField(primary_key=True)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status_reserva = models.CharField(max_length=15)
    email_doc = models.EmailField()
    sala = models.ForeignKey('Sala', on_delete=models.CASCADE, db_column='id_sala')  # Define explicitamente o nome da coluna no banco

    class Meta:
        db_table = 'reservas'

    def __str__(self):
        return f'Reserva {self.id_reserva} - {self.email_doc}'

class Reservaadm(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status_reserva = models.CharField(max_length=15)
    nome_adm = models.CharField(max_length=100)
    sala = models.IntegerField(db_column='id_sala')
    turno = models.ForeignKey('Turno', on_delete=models.CASCADE)  # Relaciona a tabela de turnos

    class Meta:
        db_table = 'reservasadmin'

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.nome_adm} - {self.turno.nome_turno}"


class Docente(models.Model):
    id_doc = models.IntegerField(primary_key=True)
    nome_doc = models.CharField(max_length=100)
    email_doc = models.EmailField(unique=True)
    senha_doc = models.CharField(max_length=6)
    cargo_doc = models.CharField(max_length=100)
    tel_doc = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'docentes'

    def __str__(self):
        return self.nome_doc

class Equipamento(models.Model):
    id_equip = models.IntegerField(primary_key=True)
    nome_equip = models.CharField(max_length=100)
    loc_equip = models.CharField(max_length=15)
    desc_equip = models.CharField(max_length=100)
    status_equip = models.CharField(max_length=100)
    quant_equip = models.IntegerField()

    class Meta:
        db_table = 'equipamentos'

    def __str__(self):
        return f'{self.nome_equip} - {self.loc_equip}'

class SalaView(models.Model):
    id_sala = models.IntegerField(primary_key=True)
    nome_sala = models.CharField(max_length=100)
    capac_sala = models.IntegerField()
    loc_sala = models.CharField(max_length=15)
    status_sala = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'view_salas'



class ReservaUltimaSemanaAdmin(models.Model):
    id_reserva = models.IntegerField(primary_key=True)
    nome_adm = models.CharField(max_length=100)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status_reserva = models.CharField(max_length=15)
    id_sala = models.IntegerField()

    class Meta:
        managed = False  # Django não gerencia esta tabela/view
        db_table = 'reservas_ultima_semana_admin'  # Nome da view no MySQL

class ReservaUltimaSemanaDocente(models.Model):
    id_reserva = models.IntegerField(primary_key=True)
    email_doc = models.CharField(max_length=100)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status_reserva = models.CharField(max_length=15)
    id_sala = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'reservas_ultima_semana_docente'

class ViewDadosDocentes(models.Model):
    id_docente = models.IntegerField(primary_key=True)
    nome_doc = models.CharField(max_length=100)
    email_doc = models.EmailField(max_length=100)
    cargo_doc = models.CharField(max_length=100)
    tel_doc = models.CharField(max_length=100, blank=True)
    id_reserva = models.IntegerField(null=True, blank=True)
    data_hora_inicio = models.DateTimeField(null=True, blank=True)
    data_hora_fim = models.DateTimeField(null=True, blank=True)
    status_reserva = models.CharField(max_length=15, null=True, blank=True)
    sala_reservada = models.CharField(max_length=100, null=True, blank=True)
    localizacao_sala = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'view_dados_docentes'

class ReservaDiaAtualAdmin(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    nome_adm = models.CharField(max_length=100)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status_reserva = models.CharField(max_length=50)
    id_sala = models.CharField(max_length=50)
    nome_sala = models.CharField(max_length=100)  # Nome da sala correspondente

    class Meta:
        managed = False  # Indica que o Django não gerencia esta tabela/view
        db_table = 'reservas_dia_atual_admin'  # Nome da view no banco de dados

    def __str__(self):
        return f"{self.nome_sala} ({self.data_hora_inicio} - {self.data_hora_fim})"

class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    nome_turno = models.CharField(max_length=50)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    class Meta:
        db_table = 'turnos'
        managed = False

    def __str__(self):
        return f"{self.nome_turno} ({self.horario_inicio} - {self.horario_fim})"

