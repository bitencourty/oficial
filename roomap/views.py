from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.http import HttpResponse
from mysql.connector import errorcode
import mysql.connector
from .models import (Reserva, Reservaadm, Equipamento, Docente, Sala, SalaView, ViewDadosDocentes,
                     ReservaUltimaSemanaAdmin, ReservaUltimaSemanaDocente, ReservaDiaAtualAdmin)
from django.contrib.auth.models import User
from .forms import DocenteForm
from django.db import connection
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import json
from django.http import JsonResponse
from django.core.mail import send_mail

def inicio_view(request):
    if request.method == 'POST':
        if 'admin_button' in request.POST:
            return redirect('loginadmin')
        elif 'docente_button' in request.POST:
            return redirect('login')
    return render(request, 'roomap/inicio.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Conexão com o banco de dados
            db_connection = mysql.connector.connect(
                host='localhost',
                user='tecmysql',
                password='devmysql',
                database='roomap'
            )
            cursor = db_connection.cursor(dictionary=True)

            # Consulta para verificar o e-mail e senha na tabela validacao
            query = "SELECT * FROM validacao WHERE email = %s AND senha = %s"
            cursor.execute(query, (email, password))
            valid_user = cursor.fetchone()

            if valid_user:
                # Armazena o e-mail na sessão para identificar o usuário logado
                request.session['email'] = valid_user['email']


                # Mensagem de sucesso e redirecionamento
                messages.success(request, f"Bem-vindo, {email}!")
                return redirect('homedocente')
            else:
                messages.error(request, "Email ou senha inválidos.")

        except mysql.connector.Error as err:
            messages.error(request, f"Erro ao acessar o banco de dados: {err}")
        finally:
            if 'db_connection' in locals():
                db_connection.close()

    return render(request, 'roomap/login.html')


def loginadmin_view(request):
    predefined_email = 'Admin@gmail.com'
    predefined_password = '1234'

    request.session['nome_adm'] = predefined_email
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Verifica se o email e a senha são os predefinidos
        if email == predefined_email and password == predefined_password:
            # Verifica se o usuário existe no banco de dados
            user, created = User.objects.get_or_create(username=email, email=email)

            if created:
                # Define uma senha padrão (não deve ser usada para autenticação real)
                user.set_password(predefined_password)
                user.save()

            # Autentica o usuário manualmente
            auth_login(request, user)
            messages.success(request, "Login bem-sucedido! Bem-vindo, admin.")
            return redirect('homeadmin')
        else:
            messages.error(request, "Falha no login. Email ou senha incorretos.")

    return render(request, 'roomap/loginadmin.html')


def cadastro_view(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)

        if form.is_valid():
            nome_doc = form.cleaned_data['nome_doc']
            email_doc = form.cleaned_data['email_doc']
            senha_doc = form.cleaned_data['senha_doc']
            cargo_doc = form.cleaned_data['cargo_doc']
            tel_doc = form.cleaned_data['tel_doc']

            try:
                # Conectar ao banco de dados
                db_connection = mysql.connector.connect(
                    host='localhost',
                    user='tecmysql',
                    password='devmysql',
                    database='roomap'
                )

                # Criar cursor
                cursor = db_connection.cursor()

                # Comando SQL para inserção
                sql = """
                        INSERT INTO docentes (nome_doc, email_doc, senha_doc, cargo_doc, tel_doc) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                docente = (nome_doc, email_doc, senha_doc, cargo_doc, tel_doc)

                # Executar a inserção
                cursor.execute(sql, docente)

                # Confirmar a transação
                db_connection.commit()

                messages.success(request, 'Docente cadastrado com sucesso!')

                # Redirecionar para a página de cadastro de reservas
                return redirect('login')

            except mysql.connector.Error as err:
                messages.error(request, f"Erro ao cadastrar docente: {err}")

            finally:
                if 'db_connection' in locals():
                    db_connection.close()

    else:
        form = DocenteForm()

    return render(request, 'roomap/cadastro.html', {'form': form})


from django.shortcuts import render
from django.db import connection
from django.utils.timezone import now
from .models import Sala

def homedocente_view(request):
    # Função para deletar reservas expiradas (implementação não mostrada aqui)
    deletar_reservas_expiradas()

    # Obter a data atual
    hoje = now().date()

    # Obter o e-mail do docente da sessão
    email_docente = request.session.get('email')
    if not email_docente:
        # Caso o e-mail não esteja na sessão, redirecionar para a página de login
        return redirect('login')

    # Query SQL para buscar reservas apenas do dia atual para o docente logado
    query = """
        SELECT id_reserva, data_hora_inicio, data_hora_fim, status_reserva, email_doc, id_sala
        FROM reservas
        WHERE DATE(data_hora_inicio) = %s AND email_doc = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [hoje, email_docente])
        reservas = cursor.fetchall()

    # Formatar os dados das reservas para uso no template
    reservas_formatadas = [
        {
            'id': reserva[0],
            'data_hora_inicio': reserva[1],
            'data_hora_fim': reserva[2],
            'status_reserva': reserva[3],
            'email_doc': reserva[4],
            'id_sala': reserva[5]
        }
        for reserva in reservas
    ]

    # Obter todas as salas do banco de dados
    salas = Sala.objects.all()

    # Criar um dicionário para rastrear o status de cada sala
    salas_status = {}
    for reserva in reservas_formatadas:
        id_sala = reserva['id_sala']
        salas_status[id_sala] = 'reservada'  # Se a sala tem uma reserva, marcamos como 'reservada'

    # Garantir que salas sem reservas sejam marcadas como 'disponível'
    total_salas = 27  # Atualize conforme o número de salas no banco
    for id_sala in range(1, total_salas + 1):
        if id_sala not in salas_status:
            salas_status[id_sala] = 'disponível'

    # Renderizar o template com os dados
    return render(request, 'roomap/homedocente.html', {
        'reservas': reservas_formatadas,  # Dados das reservas do dia atual do docente
        'salas': salas,                   # Todas as salas
        'salas_status': salas_status      # Status das salas (reservada ou disponível)
    })

def homeadmin_view(request):
    salas = Sala.objects.all()
    return render(request, 'roomap/homeadmin.html', {'salas': salas})

def reserva_sala_view(request):
    # Obtém o ID da sala a partir da URL
    sala_id = request.GET.get('sala_id')

    # Busca os dados da sala específica na view do MySQL
    sala = get_object_or_404(SalaView, id_sala=sala_id)

    # Renderiza o template com os dados da sala
    return render(request, 'roomap/reservaadmin.html', {'sala': sala})

def reserva_sala_view_docente(request):
    # Obtém o ID da sala a partir da URL
    sala_id = request.GET.get('sala_id')

    # Busca os dados da sala específica na view do MySQL
    sala = get_object_or_404(SalaView, id_sala=sala_id)

    # Renderiza o template com os dados da sala
    return render(request, 'roomap/reservadocente.html', {'sala': sala})




def reservas_do_dia_admin(request):
    reservas = ReservaDiaAtualAdmin.objects.only('nome_sala', 'data_hora_inicio', 'data_hora_fim')
    return render(request, 'roomap/homeadmin.html', {'reservas': reservas})


def reservas_do_dia_docente(request):
    return render(request, 'roomap/homedocente.html')
def inventariodocente_view(request):
    equipamentos = Equipamento.objects.all()
    return render(request, 'roomap/inventariodocente.html', {'equipamentos': equipamentos})

def inventarioadmin_view(request):
    equipamentos = Equipamento.objects.all()
    return render(request, 'roomap/inventarioadmin.html', {'equipamentos': equipamentos})

def exluir_maquina_view(request):
    return render(request, 'roomap/inventarioadmin.html')

def listafuncionarios_view(request):
    docentes = Docente.objects.all()  # Busca todos os docentes do banco de dados
    return render(request, 'roomap/listafuncionarios.html', {'docentes': docentes})

#FUNÇÃO DA PÁGINA DE ADICIONAR UMA NOVA MAQUINA (ADMIN)
def addmaquina_view(request):
    if request.method == 'POST':
        nome_equip = request.POST.get('nome_equip')
        loc_equip = request.POST.get('loc_equip')
        desc_equip = request.POST.get('desc_equip')
        status_equip = request.POST.get('status_equip')
        quant_equip = request.POST.get('quant_equip')

        try:
            # Conectar ao banco de dados
            db_connection = mysql.connector.connect(
                host='localhost',
                user='tecmysql',
                password='devmysql',
                database='roomap'
            )
            print("Conexão realizada com sucesso!")

            # Criar cursor
            cursor = db_connection.cursor()

            # Comando SQL para inserir na tabela equipamentos
            sql_equipamento = """
                    INSERT INTO equipamentos (nome_equip, loc_equip, desc_equip, status_equip, quant_equip)
                    VALUES (%s, %s, %s, %s, %s)
                """
            equipamentos = (nome_equip, loc_equip, desc_equip, status_equip, quant_equip)

            # Executar a inserção de equipamento
            cursor.execute(sql_equipamento, equipamentos)
            db_connection.commit()
            print("Equipamento inserido!")

            messages.success(request, 'Equipamento registrado com sucesso!')

            # Redirecionar para a página de equipamentos
            return redirect('addmaquina')

        except mysql.connector.Error as err:
            print(f"Erro: {err}")
            messages.error(request, 'Ocorreu um erro ao tentar registrar o equipamento.')
            return redirect('addmaquina')
        finally:
            cursor.close()
            db_connection.close()
    return render(request, 'roomap/addmaquina.html')

def addfuncionario_view(request):
    if request.method == 'POST':
        nome_doc = request.POST.get('nome_doc')
        email_doc = request.POST.get('email_doc')
        senha_doc = request.POST.get('senha_doc')
        cargo_doc = request.POST.get('cargo_doc')
        tel_doc = request.POST.get('tel_doc')

        try:
            # Conectar ao banco de dados
            db_connection = mysql.connector.connect(
                host='localhost',
                user='tecmysql',
                password='devmysql',
                database='roomap'
            )
            print("Conexão realizada com sucesso!")

            # Criar cursor
            cursor = db_connection.cursor()

            # Comando SQL para inserir na tabela docentes
            sql_docente = """
                        INSERT INTO docentes (nome_doc, email_doc, senha_doc, cargo_doc, tel_doc)
                        VALUES (%s, %s, %s, %s, %s)
                    """
            docentes = (nome_doc, email_doc, senha_doc, cargo_doc, tel_doc)

            # Executar a inserção de docente
            cursor.execute(sql_docente, docentes)
            db_connection.commit()
            print("Docente inserido!")

            messages.success(request, 'Docente registrado com sucesso!')

            # Redirecionar para a página de adicionar docente
            return redirect('addfuncionario')

        except mysql.connector.Error as err:
            print(f"Erro: {err}")
            messages.error(request, 'Ocorreu um erro ao tentar registrar o docente.')
            return redirect('addfuncionario')
        finally:
            cursor.close()
            db_connection.close()

    return render(request, 'roomap/addfuncionario.html')

def perfil_view(request):
    # Verifica se o e-mail do usuário está na sessão
    email = request.session.get('email')
    if email:
        try:
            db_connection = mysql.connector.connect(
                host='localhost',
                user='tecmysql',
                password='devmysql',
                database='roomap'
            )
            cursor = db_connection.cursor(dictionary=True)
            query = "SELECT nome_doc, cargo_doc, email_doc FROM docentes WHERE email_doc = %s"
            cursor.execute(query, (email,))
            docente_info = cursor.fetchone()

        except mysql.connector.Error as err:
            docente_info = None
        finally:
            if 'db_connection' in locals():
                db_connection.close()
    else:
        docente_info = None

    return render(request, 'roomap/perfil.html', {
        'docente_info': docente_info,
    })

def editarperfil_view(request):
    # Recupera o e-mail do docente logado (usando sessão)
    email_logado = request.session.get('email')  # Assumindo que o email do login está salvo na sessão

    if not email_logado:
        messages.error(request, 'Você precisa estar logado para editar seu perfil.')
        return redirect('login')  # Redireciona para a página de login

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='tecmysql',
            password='devmysql',
            database='roomap'
        )

        cursor = connection.cursor(dictionary=True)

        # Consulta para buscar os dados do docente logado
        select_query = "SELECT nome_doc, email_doc, cargo_doc, senha_doc FROM docentes WHERE email_doc = %s"
        cursor.execute(select_query, (email_logado,))
        docente = cursor.fetchone()

        if not docente:
            messages.error(request, 'Docente não encontrado.')
            return redirect('perfil')  # Redireciona para o perfil

        if request.method == 'POST':
            # Captura os dados enviados pelo formulário
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            cargo = request.POST.get('cargo')
            senha = request.POST.get('senha')  # Captura a nova senha do formulário

            # Atualizando os dados na tabela 'docentes'
            update_docente_query = """UPDATE docentes 
                                       SET nome_doc = %s, email_doc = %s, cargo_doc = %s, senha_doc = %s 
                                       WHERE email_doc = %s"""
            cursor.execute(update_docente_query, (nome, email, cargo, senha, email_logado))

            # Atualizando os dados na tabela 'validacao'
            update_validacao_query = """UPDATE validacao 
                                        SET email = %s, senha = %s 
                                        WHERE email = %s"""
            cursor.execute(update_validacao_query, (email, senha, email_logado))

            connection.commit()

            if cursor.rowcount > 0:
                # Atualiza o email na sessão se ele for alterado
                request.session['email'] = email
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('editarperfil')  # Redireciona para a mesma página
            else:
                messages.error(request, 'Nenhuma alteração feita.')

    except mysql.connector.Error as err:
        messages.error(request, f'Erro: {err}')
    finally:
        # Fechando a conexão com o banco
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

    return render(request, 'roomap/editarperfil.html', {'docente': docente})


def agendaadmin_view(request):
    # Buscar todas as reservas
    reservas = Reservaadm.objects.all()

    # Formatar os dados para enviar ao frontend
    reservas_formatadas = [
        {
            'data_inicio': reserva.data_hora_inicio.strftime('%Y-%m-%d'),  # Apenas a data
            'data_fim': reserva.data_hora_fim.strftime('%Y-%m-%d'),
            'status': reserva.status_reserva,
            'nome_adm': reserva.nome_adm,
            'id_sala': reserva.sala
        }
        for reserva in reservas
    ]

    return render(request, 'roomap/agendaadmin.html', {'reservas': reservas_formatadas})

def salas_view(request):
    salas = Sala.objects.all()
    return render(request, 'roomap/salas.html', {'salas': salas})

from django.db import connection
from django.shortcuts import render

def mapa_view(request):
    deletar_reservas_expiradas()

    # Query SQL para buscar todas as reservas (docentes e admin)
    query = """
        SELECT id_reserva, data_hora_inicio, data_hora_fim, status_reserva, email_doc, id_sala
        FROM reservas
        UNION
        SELECT id_reserva, data_hora_inicio, data_hora_fim, status_reserva, nome_adm AS email_doc, id_sala
        FROM reservasadmin
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        reservas = cursor.fetchall()

    # Formatar as reservas em um dicionário
    reservas_formatadas = [
        {
            'id': reserva[0],
            'data_hora_inicio': reserva[1],
            'data_hora_fim': reserva[2],
            'status_reserva': reserva[3],
            'email_doc': reserva[4],  # Aqui pode ser o email do docente ou nome do admin
            'id_sala': reserva[5]
        }
        for reserva in reservas
    ]

    # Criar um dicionário para rastrear o status de cada sala
    salas_status = {}
    for reserva in reservas_formatadas:
        id_sala = reserva['id_sala']
        salas_status[id_sala] = 'reservada'  # Se há uma reserva, marcamos como 'reservada'

    # Garantir que salas sem reservas sejam marcadas como 'disponível'
    total_salas = 27  # Atualize este número de acordo com a quantidade total de salas no mapa
    for id_sala in range(1, total_salas + 1):
        if id_sala not in salas_status:
            salas_status[id_sala] = 'disponível'

    return render(request, 'roomap/mapa.html', {
        'tabelas': reservas_formatadas,
        'salas_status': salas_status  # Passar o status das salas ao template
    })
def deletar_reservas_expiradas():
    agora = datetime.now()
    with connection.cursor() as cursor:

        # Excluir todas as reservas onde data_hora_fim já passou
        cursor.execute("DELETE FROM reservas WHERE data_hora_fim < %s", [agora]) # função que deleta as reservas inspiradas.

def relatorio_admin(request):
    # Verifica se o administrador está logado
    email_logado = request.session.get('email')  # Email do admin logado

    if not email_logado:
        mensagem = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .message-container {
                    text-align: center;
                    background: #ffffff;
                    border-radius: 10px;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                    max-width: 600px;
                    width: 90%;
                }
                .message-container h1 {
                    font-size: 32px;
                    color: #333;
                    margin-bottom: 20px;
                }
                .message-container p {
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 30px;
                }
                .message-container a {
                    text-decoration: none;
                    color: #fff;
                    background: #007BFF;
                    padding: 15px 30px;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                .message-container a:hover {
                    background: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="message-container">
                <h1>Acesso Negado</h1>
                <p>Você precisa estar logado como administrador para acessar esta funcionalidade.</p>
                <a href="/homeadmin/">Voltar para Home</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(mensagem)

    # Filtrar reservas utilizando a view MySQL e o email do administrador
    reservas = ReservaUltimaSemanaAdmin.objects.filter(nome_adm=email_logado)

    if not reservas.exists():
        mensagem = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .message-container {
                    text-align: center;
                    background: #ffffff;
                    border-radius: 10px;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                    max-width: 600px;
                    width: 90%;
                }
                .message-container h1 {
                    font-size: 32px;
                    color: #333;
                    margin-bottom: 20px;
                }
                .message-container p {
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 30px;
                }
                .message-container a {
                    text-decoration: none;
                    color: #fff;
                    background: #007BFF;
                    padding: 15px 30px;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                .message-container a:hover {
                    background: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="message-container">
                <h1>Nenhuma Reserva Encontrada</h1>
                <p>Não há reservas registradas para este administrador na última semana.</p>
                <a href="/homeadmin/">Voltar para Home</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(mensagem)

    # Caso existam reservas, gere o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_admin.pdf"'

    # Configura o PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']

    elements.append(Paragraph("Relatório de Reservas - Administrador", title_style))

    data = [["ID", "Data Início", "Data Fim", "Status", "Sala"]]
    for reserva in reservas:
        data.append([
            reserva.id_reserva,
            reserva.data_hora_inicio.strftime("%d/%m/%Y %H:%M"),
            reserva.data_hora_fim.strftime("%d/%m/%Y %H:%M"),
            reserva.status_reserva,
            reserva.id_sala,
        ])

    table = Table(data)
    elements.append(table)

    doc.build(elements)
    return response

def relatorio_docente(request):
    # Verifica se o docente está logado
    email_logado = request.session.get('email')  # Email do docente logado

    if not email_logado:
        mensagem = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .message-container {
                    text-align: center;
                    background: #ffffff;
                    border-radius: 10px;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                    max-width: 600px;
                    width: 90%;
                }
                .message-container h1 {
                    font-size: 32px;
                    color: #333;
                    margin-bottom: 20px;
                }
                .message-container p {
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 30px;
                }
                .message-container a {
                    text-decoration: none;
                    color: #fff;
                    background: #007BFF;
                    padding: 15px 30px;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                .message-container a:hover {
                    background: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="message-container">
                <h1>Acesso Negado</h1>
                <p>Você precisa estar logado para acessar esta funcionalidade.</p>
                <a href="/homedocente/">Voltar para Home</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(mensagem)

    # Filtrar reservas utilizando a view MySQL e o email do docente
    reservas = ReservaUltimaSemanaDocente.objects.filter(nome_doc=email_logado)

    if not reservas.exists():
        mensagem = """
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .message-container {
                    text-align: center;
                    background: #ffffff;
                    border-radius: 10px;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
                    max-width: 600px;
                    width: 90%;
                }
                .message-container h1 {
                    font-size: 32px;
                    color: #333;
                    margin-bottom: 20px;
                }
                .message-container p {
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 30px;
                }
                .message-container a {
                    text-decoration: none;
                    color: #fff;
                    background: #007BFF;
                    padding: 15px 30px;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                .message-container a:hover {
                    background: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="message-container">
                <h1>Nenhuma Reserva Encontrada</h1>
                <p>Não há reservas registradas para este docente na última semana.</p>
                <a href="/homedocente/">Voltar para Home</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(mensagem)

    # Caso existam reservas, gere o PDF (continuar lógica de geração do PDF)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_semana.pdf"'

    # Configura o PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Title']

    elements.append(Paragraph("Relatório de Reservas - Semana Atual", title_style))

    data = [["ID", "Data Início", "Data Fim", "Status", "Sala"]]
    for reserva in reservas:
        data.append([
            reserva.id_reserva,
            reserva.data_hora_inicio.strftime("%d/%m/%Y %H:%M"),
            reserva.data_hora_fim.strftime("%d/%m/%Y %H:%M"),
            reserva.status_reserva,
            reserva.id_sala,
        ])

    table = Table(data)
    elements.append(table)

    doc.build(elements)
    return response



def send_help_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "")

        if message.strip():
            send_mail(
                subject="Ajuda Solicitada",
                message=message,
                from_email="lucasbrazao@aluno.senai.br",  # Substitua pelo seu e-mail
                recipient_list=["lucasbrazao@aluno.senai.br"],  # Substitua pelo e-mail que receberá a mensagem
            )
            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"error": "Mensagem vazia"}, status=400)
    return JsonResponse({"error": "Método não permitido"}, status=405)



from datetime import date
from django.shortcuts import render
from .models import Reserva



def reservadocente_view(request):
    if request.method == 'POST':
        email_doc = request.POST.get('email_doc')  # email que do docente
        if not email_doc:
            messages.error(request, "O e-mail não foi encontrado. Faça login novamente.")
            return redirect('login')  # Redireciona para a página de login

        data_hora_inicio = request.POST.get('data_hora_inicio')  # Data e hora de início
        data_hora_fim = request.POST.get('data_hora_fim')  # Data e hora de fim
        id_sala = request.POST.get('id_sala')  # ID da sala

        # Definindo o status da reserva como "Confirmada" automaticamente
        status_reserva = 'Confirmada'

        try:
            # Conectar ao banco de dados
            db_connection = mysql.connector.connect(
                host='localhost',
                user='tecmysql',
                password='devmysql',
                database='roomap'
            )
            print("Conexão realizada com sucesso!")

            # Criar cursor
            cursor = db_connection.cursor()

            # Comando SQL para inserção
            sql = """
                    INSERT INTO reservas (data_hora_inicio, data_hora_fim, status_reserva, email_doc, id_sala) 
                    VALUES (%s, %s, %s, %s, %s)
                """
            reservas = (data_hora_inicio, data_hora_fim, status_reserva, email_doc, id_sala)

            # Executar a inserção
            cursor.execute(sql, reservas)

            # Confirmar a transação
            db_connection.commit()
            print("Registro inserido!")
            messages.success(request, 'Reserva feita com sucesso!')

            # Redirecionar para a mesma página, mas com a mensagem na sessão
            return redirect('homedocente')

        except mysql.connector.Error as error:
            # Tratar erros específicos de banco de dados
            if error.errno == errorcode.ER_BAD_DB_ERROR:
                return HttpResponse("Erro: O banco de dados não existe.")
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                return HttpResponse("Erro: Nome de usuário ou senha incorretos.")
            else:
                return HttpResponse(f"Erro desconhecido: {error}")

        finally:
            if 'db_connection' in locals() and db_connection.is_connected():
                cursor.close()
                db_connection.close()
                print("Conexão encerrada.")
    #passa para o campo do email, o email logado para que o docente não precise colocar o email de novo.
    email_doc = request.session.get('email', '')
    return render(request, 'roomap/reservadocente.html')

def agenda_view(request):
    return render(request, 'roomap/agenda.html')


def reservaadmin_view(request):
    if request.method == 'POST':
        nome_adm = request.POST.get('nome_adm')
        if not nome_adm:
            messages.error(request, "O e-mail não foi encontrado. Faça login novamente.")
            return redirect('loginadmin')  # Redireciona para a página de login
        data_hora_inicio = request.POST.get('data_hora_inicio')
        data_hora_fim = request.POST.get('data_hora_fim')
        id_sala = request.POST.get('id_sala')

        status_reserva = 'Confirmada'

        try:
            # Conectar ao banco de dados
            db_connection = mysql.connector.connect(
                host='localhost',
                user='tecmysql',
                password='devmysql',
                database='roomap'
            )
            print("Conexão realizada com sucesso!")

            cursor = db_connection.cursor()

            sql = """
                    INSERT INTO reservasadmin (data_hora_inicio, data_hora_fim, status_reserva, nome_adm, id_sala) 
                    VALUES (%s, %s, %s, %s, %s)
                """
            reservas = (data_hora_inicio, data_hora_fim, status_reserva, nome_adm, id_sala)

            cursor.execute(sql, reservas)

            db_connection.commit()
            print("Registro inserido!")
            messages.success(request, 'Reserva feita com sucesso!')

            return redirect('homeadmin')

        except mysql.connector.Error as error:
            if error.errno == errorcode.ER_BAD_DB_ERROR:
                return HttpResponse("Erro: O banco de dados não existe.")
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                return HttpResponse("Erro: Nome de usuário ou senha incorretos.")
            else:
                return HttpResponse(f"Erro desconhecido: {error}")

        finally:
            if 'db_connection' in locals() and db_connection.is_connected():
                cursor.close()
                db_connection.close()
                print("Conexão encerrada.")

    return render(request, 'roomap/reservaadmin.html')