from flask import redirect, url_for, jsonify
import tkinter as tk
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import datetime as dt
import urllib
import time
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils.database import Database
import threading
from utils.busca_arquivos import buscar_anexos
from wpp_automatizado import enviar_mensagens_whatsapp
from wpp_automatizado import gerar_qrcode
from utils.eMail_automatizado import enviar_email
import webbrowser
import threading
import json


app = Flask(__name__)


def open_browser():
    time.sleep(1.5)  # Small delay to ensure Flask server is running
    webbrowser.open("http://127.0.0.1:5000")


def data_agora():
    data_hora_atual = datetime.now()
    # Formata para DD/MM/YYYY HH:MM
    data_hora_formatada = data_hora_atual.strftime("%d/%m/%Y %H:%M")
    return data_hora_formatada

# ---------------------------------------------------------------------------------------
#                                  LISTAS
# ---------------------------------------------------------------------------------------


def lista_grupos():
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os dados.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()

    # Inserir dados na tabela:
    c.execute("SELECT *, oid FROM empresas WHERE Id_user = ?",
              (usuario_autenticado,))
    empresas_cadastradas = c.fetchall()
    # print(pessoas_cadastradas)
    empresas_cadastradas = pd.DataFrame(empresas_cadastradas, columns=[
                                        'Empresa', 'Grupo', 'Atividade', 'Folha', 'Email', 'Marcar', 'Log_alteracao', 'id_empresa', 'Id_user'])

    conexao.close()

    lista_grupos = empresas_cadastradas['Grupo'].unique()
    lista_grupos = sorted(lista_grupos)  # Ordenação alfabetica

    # print(f"lista_grupos:"+lista_grupos)

    return ['']+list(lista_grupos)


def lista_empresas():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar as empresas.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()

    # Inserir dados na tabela:
    c.execute("SELECT *, oid FROM empresas WHERE Id_user = ?",
              (usuario_autenticado,))
    empresas_cadastradas = c.fetchall()
    # print(pessoas_cadastradas)
    empresas_cadastradas = pd.DataFrame(empresas_cadastradas, columns=[
                                        'Empresa', 'Grupo', 'Atividade', 'Folha', 'Email', 'Marcar', 'Log_alteracao', 'id_empresa', 'Id_user'])

    conexao.close()

    lista_empresas = empresas_cadastradas['Empresa'].unique()
    lista_empresas = sorted(lista_empresas)  # Ordenação alfabetica

    # print(f"lista_empresas:"+lista_empresas)

    return ['']+list(lista_empresas)


def lista_atividades():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os dados.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()

    # Inserir dados na tabela:
    c.execute("SELECT *, oid FROM empresas WHERE Id_user = ?",
              (usuario_autenticado,))

    empresas_cadastradas = c.fetchall()
    # print(pessoas_cadastradas)
    empresas_cadastradas = pd.DataFrame(empresas_cadastradas, columns=[
                                        'Empresa', 'Grupo', 'Atividade', 'Folha', 'Email', 'Marcar', 'Log_alteracao', 'id_empresa', 'Id_user'])

    conexao.close()

    lista_atividades = empresas_cadastradas['Atividade'].unique()
    lista_atividades = sorted(lista_atividades)  # Ordenação alfabetica

    # print(f"lista_atividades:"+lista_atividades)

    return ['']+list(lista_atividades)


def lista_folha():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os dados.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()

    # Inserir dados na tabela:
    c.execute("SELECT *, oid FROM empresas WHERE Id_user = ?",
              (usuario_autenticado,))
    empresas_cadastradas = c.fetchall()
    # print(pessoas_cadastradas)
    empresas_cadastradas = pd.DataFrame(empresas_cadastradas, columns=[
                                        'Empresa', 'Grupo', 'Atividade', 'Folha', 'Email', 'Marcar', 'Log_alteracao', 'id_empresa', 'Id_user'])

    conexao.close()

    lista_folha = empresas_cadastradas['Folha'].unique()
    lista_folha = sorted(lista_folha)  # Ordenação alfabetica

    # print(f"Lista de folha:"+lista_folha)

    return ['']+list(lista_folha)


def Lista_assunto():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os dados.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()

    # Inserir dados na tabela:
    c.execute("SELECT *, oid FROM mensagens_email WHERE Id_user = ?",
              (usuario_autenticado,))
    mensagens_cadastradas = c.fetchall()
    # print(pessoas_cadastradas)
    mensagens_cadastradas = pd.DataFrame(mensagens_cadastradas, columns=[
                                         'Assunto', 'Corpo', 'Log_alteracao', 'id_mensagem', 'Id_user'])

    conexao.close()

    lista_assuntos = mensagens_cadastradas['Assunto'].unique()
    lista_assuntos = sorted(lista_assuntos)  # Ordenação alfabetica

    # print(f"Lista de assuntos:"+lista_assuntos)

    return ['']+list(lista_assuntos)

# lista_anexo_tmp = ['']+list(['Sim'])
lista_anexo_tmp = list(['Específico por cliente','Fixo','Nenhum'])
lista_marcadas_tmp = ['']+list(['Sim'])

lista_tipo_anexo = list(['Específico','Fixo'])
# ----------------------------------------------------------------------------------
#                               JOIN TABELA
# ----------------------------------------------------------------------------------


def join_tabelas():
    buscar_anexos()  # EXECUTAR NO ARQUIVO busca_arquivos.py

    with sqlite3.connect('cadastro.db') as conexao:
        c = conexao.cursor()
        assunto_filtro = request.form.get('Assunto', '').strip()
        conteudo_campo_anexo = request.form.get('Anexo', '').strip()

        # Se o campo "Anexo" for "Fixo", buscar anexos diretamente da tabela original
        caminhos_anexos_fixo = ''
        if conteudo_campo_anexo == "Fixo":
            c.execute("""
                SELECT GROUP_CONCAT(Caminho_anexo, ', ') 
                FROM anexos_email 
                WHERE Assunto = ?
            """, (assunto_filtro,))
            resultado = c.fetchone()
            caminhos_anexos_fixo = resultado[0] if resultado and resultado[0] else ''

        # Monta a base da query
        query = """
            SELECT empresas.Empresa,
                   empresas.Grupo,
                   empresas.Atividade,
                   empresas.Folha,
                   empresas.Marcar,
                   pessoas.Pessoa,
                   pessoas.Telefone,
                   ? AS Caminhos_anexos,
                   ? AS Assunto,
                   mensagens_email.Corpo,
                   GROUP_CONCAT(empresas.Email, ', ') AS Emails
            FROM empresas
            LEFT JOIN pessoas ON empresas.Empresa = pessoas.Empresa
            LEFT JOIN mensagens_email ON mensagens_email.Assunto = ?
        """

        if conteudo_campo_anexo != "Fixo":
            # Se não for fixo, usa a tabela temporária com os anexos da função buscar_anexos
            query = """
                SELECT empresas.Empresa,
                       empresas.Grupo,
                       empresas.Atividade,
                       empresas.Folha,
                       empresas.Marcar,
                       pessoas.Pessoa,
                       pessoas.Telefone,
                       GROUP_CONCAT(anexos_email_temp.Caminho_anexo, ', ') AS Caminhos_anexos,
                       ? AS Assunto,
                       mensagens_email.Corpo,
                       GROUP_CONCAT(empresas.Email, ', ') AS Emails
                FROM empresas
                LEFT JOIN pessoas ON empresas.Empresa = pessoas.Empresa
                LEFT JOIN anexos_email_temp ON empresas.Empresa = anexos_email_temp.Empresa AND anexos_email_temp.Assunto = ?
                LEFT JOIN mensagens_email ON mensagens_email.Assunto = ?
            """

            if conteudo_campo_anexo == "Específico por cliente":
                query += """
                    WHERE anexos_email_temp.Caminho_anexo IS NOT NULL 
                      AND anexos_email_temp.Caminho_anexo <> ''
                """

        query += """
            GROUP BY empresas.Empresa, empresas.Grupo, empresas.Atividade, empresas.Folha, empresas.Marcar,
                     pessoas.Pessoa, pessoas.Telefone, mensagens_email.Corpo
        """

        # Define os parâmetros da consulta
        if conteudo_campo_anexo == "Fixo":
            c.execute(query, (caminhos_anexos_fixo, assunto_filtro, assunto_filtro))
        else:
            c.execute(query, (assunto_filtro, assunto_filtro, assunto_filtro))

        resultado_left_join = c.fetchall()
        colunas = [descricao[0] for descricao in c.description]
        df = pd.DataFrame(resultado_left_join, columns=colunas)

        # Limpa duplicatas nos anexos e e-mails
        df['Caminhos_anexos'] = df['Caminhos_anexos'].apply(
            lambda x: ', '.join(set(x.split(', '))) if x else '')
        df['Emails'] = df['Emails'].apply(
            lambda x: ', '.join(set(x.split(', '))) if x else '')

        df.to_excel("resultado_join.xlsx", index=False)
        print("✅ Dados exportados com sucesso para 'resultado_join.xlsx'.")
        return df



# ----------------------------------------------------------------------------------
#                               FILTRAR TABELA
# ----------------------------------------------------------------------------------

# Função para processar filtros e gerar o DataFrame filtrado


def processar_filtros(Ultima_linha_banco):

    Ultimo_grupo = Ultima_linha_banco['Grupo']
    Ultimo_atividade = Ultima_linha_banco['Atividade']
    Ultimo_possui_folha = Ultima_linha_banco['Folha']
    Ultimo_marcar = Ultima_linha_banco['Marcar']
    Ultimo_assunto = Ultima_linha_banco['Assunto']

    resultado_join = join_tabelas()
    df = pd.DataFrame(resultado_join)

    # Start filtering with the full DataFrame `df`
    df_filtrado = df

    # Apply each filter condition in sequence
    if Ultimo_assunto:
        df_filtrado = df_filtrado[df_filtrado["Assunto"] == Ultimo_assunto]

    if Ultimo_grupo:
        df_filtrado = df_filtrado[df_filtrado["Grupo"] == Ultimo_grupo]

    if Ultimo_possui_folha == "Sim":
        df_filtrado = df_filtrado[df_filtrado["Folha"] != ""]
    elif Ultimo_possui_folha:  # Handle other cases of `Ultimo_possui_folha`
        df_filtrado = df_filtrado[df_filtrado["Folha"] == Ultimo_possui_folha]

    if Ultimo_atividade:
        df_filtrado = df_filtrado[df_filtrado["Atividade"] == Ultimo_atividade]

    if Ultimo_marcar:
        df_filtrado = df_filtrado[df_filtrado["Marcar"] == Ultimo_marcar]

    # Obtém o usuário autenticado da sessão
    usuario_autenticado = session['usuario']
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def limpar_tabela():
        """Função para limpar a tabela antes de inserir novos dados."""
        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        c.execute("DELETE FROM dados_enviar")  # Remove todos os registros
        conexao.commit()
        conexao.close()
        # print("✅ Tabela 'dados_enviar' limpa com sucesso!")
        # incluir inserção do banco de dados aqui:

    # Datas
    today = datetime.now()
    primeiro_dia_do_mes_atual = today.replace(day=1)
    mes_anterior_data = primeiro_dia_do_mes_atual - timedelta(days=1)

    mes_atual = today.strftime('%m/%Y')
    mes_anterior = mes_anterior_data.strftime('%m/%Y')
    ano_atual = today.strftime('%Y')
    ano_anterior = today.replace(year=today.year - 1).strftime('%Y')

    # Função para substituir marcadores
    def substituir_marcadores(texto, mes_atual, mes_anterior, ano_atual, ano_anterior, empresa, pessoa):
        return (
            texto.replace("mes_ant_", mes_anterior)
                 .replace("mes_", mes_atual)
                 .replace("ano_", ano_atual)
                 .replace("ano_ant_", ano_anterior)
                 .replace("emp_", empresa)
                 .replace("pessoa_", pessoa)
                 .replace("\\n", "\n")
        )

    def inserir_dados(df_filtrado, usuario_autenticado, log_alteracao):
        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        # Iterar sobre todas as linhas do DataFrame

        # Pega o valor exato selecionado no formulário
        anexo_selecionado = request.form.get('Anexo', '')

        # Para depuração: veja no seu console o que o formulário está enviando
        print(f"Opção de anexo selecionada no formulário: '{anexo_selecionado}'")


        for _, row in df_filtrado.iterrows():
            empresa = str(row["Empresa"]).upper(
            ) if pd.notna(row["Empresa"]) else ""
            grupo = str(row["Grupo"]) if pd.notna(row["Grupo"]) else ""
            atividade = str(row["Atividade"]) if pd.notna(
                row["Atividade"]) else ""
            folha = str(row["Folha"]) if pd.notna(row["Folha"]) else ""
            emails = str(row["Emails"]).lower(
            ) if pd.notna(row["Emails"]) else ""
            marcar = str(row["Marcar"]) if pd.notna(row["Marcar"]) else ""
            caminhos_anexos = str(row["Caminhos_anexos"]) if pd.notna(
                row["Caminhos_anexos"]) else ""
            assunto = str(row["Assunto"]) if pd.notna(row["Assunto"]) else ""
            corpo = str(row["Corpo"]) if pd.notna(row["Corpo"]) else ""
            pessoa = str(row["Pessoa"]) if pd.notna(row["Pessoa"]) else ""
            telefone = str(row["Telefone"]) if pd.notna(row["Telefone"]) else ""

            # Só preenche caminhos_anexos se o valor for exatamente "Específico por cliente"
            if anexo_selecionado == "Específico por cliente":
                caminhos_anexos = str(row["Caminhos_anexos"]) if pd.notna(row["Caminhos_anexos"]) else ""
                if isinstance(caminhos_anexos, list):
                    caminhos_anexos = ",".join(caminhos_anexos)
            else:
                caminhos_anexos = ""  # garante que não será gravado nada

            corpo = substituir_marcadores(corpo, mes_atual, mes_anterior, ano_atual, ano_anterior, empresa, pessoa)
            if telefone != "":
                c.execute("""
                    INSERT INTO dados_enviar 
                    (Empresa, Grupo, Atividade, Folha, Emails, Marcar, Caminhos_anexos, Assunto, Corpo, Pessoa, Telefone, Log_alteracao, Id_user) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (empresa, grupo, atividade, folha, emails, marcar, caminhos_anexos, assunto, corpo, pessoa, telefone, log_alteracao, usuario_autenticado))

        conexao.commit()
        conexao.close()

    limpar_tabela()  # Limpa a tabela antes da inserção
    inserir_dados(df_filtrado, usuario_autenticado,
                  log_alteracao)  # Insere os novos dados

    df_filtrado.to_excel('dados_filtrados.xlsx', index=False)
    print("✅ Dados exportados com sucesso para 'dados_filtrados.xlsx'.")

    return df_filtrado

# ----------------------------------------------------------------------------------
#                               GRAVAR DADOS A ENVIAR
# ----------------------------------------------------------------------------------


@app.route('/gravar_dados_a_enviar', methods=['POST'])
def gravar_dados_a_enviar():
    # 1. Verificação de campos vazios e preenchimento
    # print(request.form)  # Exibe os dados recebidos
    if all(not request.form.get(field) for field in ['Assunto']):
        return jsonify({"error": "Selecione algum destinatário, retorne e tente novamente"}), 400

    Data_envio = dt.datetime.now().strftime("%d/%m/%Y %H:%M")

    # 3. Inserção no banco de dados e recuperação dos dados inseridos
    with sqlite3.connect('cadastro.db') as conexao:
        # Verifica se o usuário está autenticado
        if 'usuario' not in session:
            flash('Você precisa estar autenticado para acessar os dados.', 'error')
            return []

        # Obtém o nome do usuário autenticado
        usuario_autenticado = session['usuario']
        c = conexao.cursor()
        c.execute("""
            INSERT INTO dados_tela_envio 
            (Grupo, Atividade, Folha, Marcar, Anexo, Assunto, Log_alteracao, Id_user) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form.get('grupo', ''),
            request.form.get('atividade', ''),
            request.form.get('folha', ''),
            request.form.get('Selecionar', ''),
            request.form.get('Anexo', ''),
            request.form.get('Assunto', ''),
            Data_envio,
            usuario_autenticado
        ))

        conexao.commit()

        # Obtém o nome do usuário autenticado
        usuario_autenticado = session['usuario']
        # Seleciona a última linha inserida para os filtros
        c.execute("SELECT *, oid FROM dados_tela_envio WHERE Id_user = ? ORDER BY oid DESC LIMIT 1",
                  (usuario_autenticado,))
        Ultima_linha_banco = c.fetchone()
        dados_enviar = pd.DataFrame([Ultima_linha_banco], columns=[
                                    'Grupo', 'Atividade', 'Folha', 'Marcar', 'Anexo', 'Assunto', 'Log_alteracao', 'Id_user', 'oid'])
    


    # 5. Realiza o join e aplica filtros para o destinatário
    df_filtrado = processar_filtros(dados_enviar.iloc[-1])

    # 6. Exporta o DataFrame filtrado para Excel
    df_filtrado.to_excel('enviar_temp.xlsx', index=False)
    print("✅ Dados exportados com sucesso para 'enviar_temp.xlsx'.")


    """
    Redireciona o usuário com base na seleção do campo 'Anexo' em um formulário.
    """
    # Pega o valor do campo 'Anexo'. Se não existir, usa uma string vazia.
    tem_anexo = request.form.get('Anexo', '')

    # Verifica se o valor é "Sim"
    if tem_anexo == "Específico por cliente":
        # Se for "Sim", redireciona para a página de anexos
        return redirect(url_for('visualizar_anexos'))
    else:
        # Caso contrário, redireciona para a página de destinatários
        return redirect(url_for('visualizar_destinatarios'))



    # # 7. Redireciona para a rota visualizar_anexos
    # return redirect(url_for('visualizar_anexos'))

    # 8. Executa o envio de mensagens, se necessário
    # enviar_email()  # EXECUTA DENTRO DO ARQUIVO



    # Executar
    
    


# ----------------------------------------------------------------------------------
#                               ROTAS INICIAIS
# ----------------------------------------------------------------------------------
app.secret_key = os.urandom(24)
db = Database()

# Simulando um usuário autenticado
USUARIO_AUTENTICADO = False


@app.route('/')
def index():
    return render_template('login.html')

# ----------------------------------------------------------------------------------
#                               TELA DE LOGIN
# ----------------------------------------------------------------------------------


import threading

@app.route('/login', methods=['POST'])
def login():
    global USUARIO_AUTENTICADO
    usuario = request.form['usuario']
    senha = request.form['senha']

    if db.verificar_login(usuario, senha):
        USUARIO_AUTENTICADO = True
        session['usuario'] = usuario
        flash('Login realizado com sucesso!', 'success')

        # Rodar geração de QR code em background
        threading.Thread(target=gerar_qrcode).start()

        return redirect(url_for('validacao_qrcode'))
    else:
        flash('Credenciais inválidas. Tente novamente.', 'error')
        return redirect(url_for('index'))


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']

        if senha != confirmar_senha:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('cadastro'))

        if db.buscar_usuario(usuario):
            flash('Usuário já existe!', 'error')
            return redirect(url_for('cadastro'))

        if db.cadastrar_usuario(nome, usuario, senha):
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Erro ao cadastrar usuário!', 'error')
            return redirect(url_for('cadastro'))

    return render_template('cadastro_usuarios.html')

# #----------------------------------------------------------------------------------
# #                               AUTÊNTICAÇÃO QR CODE
# #----------------------------------------------------------------------------------

import os # Garanta que 'os' está importado no topo do seu arquivo
import json # Garanta que 'json' está importado no topo do seu arquivo

@app.route("/validacao_qrcode")
def validacao_qrcode():
    status_path = os.path.join(app.static_folder, 'status.json')
    logado = False
    data_qr = "Arquivo de status não encontrado"
    
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
            logado = status_data.get('logado', False)
            data_qr = status_data.get('data', 'Data não disponível')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao ler status.json: {e}")

    return render_template("validacao_qrcode.html", logado=logado, data_qr=data_qr)

@app.route("/prosseguir", methods=["POST"])
def prosseguir():
    return redirect(url_for("envio_mensagem")) 


# #----------------------------------------------------------------------------------
# #                               TELA DE ENVIAR MENSAGEM
# #----------------------------------------------------------------------------------
@app.route('/envio_mensagem')
def envio_mensagem():
    if not USUARIO_AUTENTICADO:
        return redirect(url_for('index'))

    # Carrega status do QR Code
    status_path = os.path.join(app.static_folder, 'status.json')
    try:
        with open(status_path, 'r') as f:
            status_data = json.load(f)
            logado = status_data.get('logado', False)
            data_status = status_data.get('data', 'Data não disponível')
    except:
        logado = False
        data_status = 'Arquivo não encontrado'

    return render_template('envio_mensagem_email.html',
                           lista_gruposBD=lista_grupos(),
                           lista_atividadesBD=lista_atividades(),
                           lista_assuntoBD=Lista_assunto(),
                           lista_folhaBD=lista_folha(),
                           lista_anexo=lista_anexo_tmp,
                           lista_selecionar=lista_marcadas_tmp,
                           logado=logado,
                           data_qr=data_status)


# ------------------------------------------------------------------------
#                               CADASTRO MENSAGENS
# ------------------------------------------------------------------------


@app.route('/cadastro_email', methods=['GET', 'POST'])
def cadastro_email():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Lógica para POST - cadastro de uma nova mensagem
    if request.method == 'POST':
        if 'usuario' not in session:
            flash('Você precisa estar autenticado para realizar essa operação.', 'error')
            return redirect(url_for('index'))

        # Obtém o usuário autenticado da sessão
        usuario_autenticado = session['usuario']

        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        c.execute("INSERT INTO mensagens_email (Assunto, Corpo, Log_alteracao, Id_user) VALUES (?, ?, ?, ?)",
                  (request.form['Assunto'], request.form['Corpo'], log_alteracao, usuario_autenticado))
        conexao.commit()
        conexao.close()

    # Lógica para GET - exibir o formulário com as mensagens existentes
    if USUARIO_AUTENTICADO:
        mensagens = atualizar_treeview_mensagem()
        return render_template('cadastro_email.html', mensagens=mensagens)
    else:
        return redirect(url_for('index'))


@app.route('/editar_email/<int:id_mensagem>', methods=['POST'])
def editar_mensagem_email(id_mensagem):
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if request.method == 'POST':
        Assunto = request.form['Assunto']
        Corpo = request.form['Corpo']

        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        c.execute("UPDATE mensagens_email SET Assunto=?, Corpo=?, Log_alteracao=? WHERE rowid=?",
                  (Assunto, Corpo, log_alteracao, id_mensagem))

        conexao.commit()
        conexao.close()

    return redirect(url_for('cadastro_email'))


@app.route('/excluir_email/<int:id_mensagem>')
def excluir_mensagem_email(id_mensagem):
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute("DELETE FROM mensagens_email WHERE rowid=?", (id_mensagem,))
    conexao.commit()
    conexao.close()

    return redirect(url_for('cadastro_email'))


def atualizar_treeview_mensagem():
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar as empresas.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute("SELECT rowid, Assunto, Corpo FROM mensagens_email WHERE Id_user = ?",
              (usuario_autenticado,))
    mensagens = c.fetchall()
    conexao.close()
    return mensagens

# ------------------------------------------------------------------------
#                               CADASTRO EMPRESAS
# ------------------------------------------------------------------------


def atualizar_treeview_empresa():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar as empresas.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    # Conecta ao banco de dados
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    # Seleciona todas as empresas do banco de dados
    c.execute("SELECT rowid, * FROM empresas WHERE Id_user = ?",
              (usuario_autenticado,))

    empresas = c.fetchall()  # Obtém todas as linhas da consulta
    conexao.close()  # Fecha a conexão com o banco de dados
    return empresas  # Retorna a lista de empresas


lista_Grupo_cadastro_empresa = [
    '']+sorted(list(["MEI", "Regime_Normal", "Simples", "Imposto de renda"]))
lista_atividade_cadastro_emp = [''] + \
    sorted(list(["Comércio", "Serviço", "Ambos"]))
# Sorted é para ordenação alfabetica
lista_folha_cadastro_emp = [''] + \
    sorted(list(['Colaborador', 'Pró-labore', 'Ambos']))

# GET é usado para obter recursos do servidor


@app.route('/cadastro_empresas', methods=['GET'])
def exibir_formulario_cadastro_empresas():
    if USUARIO_AUTENTICADO:
        empresas = atualizar_treeview_empresa()
        return render_template('cadastro_empresas.html', empresas=empresas,
                               lista_folha=lista_folha_cadastro_emp,
                               lista_atividade=lista_atividade_cadastro_emp,
                               lista_grupo=lista_Grupo_cadastro_empresa,
                               )
    else:
        return redirect(url_for('index'))


# POST é usado para enviar dados para o servidor
@app.route('/cadastro_empresas', methods=['POST'])
def cadastro_empresas():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        if 'usuario' not in session:
            flash('Você precisa estar autenticado para realizar essa operação.', 'error')
            return redirect(url_for('index'))

        # Obtém o usuário autenticado da sessão
        usuario_autenticado = session['usuario']

        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        c.execute("INSERT INTO empresas VALUES (:Empresa,:Grupo,:Atividade, :Folha, :Email, :Marcar,:Log_alteracao, :Id_user)",
                  {
                      'Empresa': request.form['Empresa'].upper(),
                      'Grupo': request.form['Grupo'],
                      'Atividade': request.form['Atividade'],
                      'Folha': request.form['Folha'],
                      'Email': request.form['Email'].lower(),
                      'Marcar': request.form['Marcar'],
                      'Log_alteracao': log_alteracao,
                      'Id_user': usuario_autenticado
                  })
        conexao.commit()
        conexao.close()

        empresas = atualizar_treeview_empresa()
        # return render_template('cadastro_empresas.html',empresas=empresas)
        return render_template('cadastro_empresas.html', empresas=empresas, lista_folha=lista_folha_cadastro_emp, lista_grupo=lista_Grupo_cadastro_empresa, lista_atividade=lista_atividade_cadastro_emp)


@app.route('/editar_empresa', methods=['POST'])
def editar_empresa():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Use .get() to allow Marcar to be optional
    id_empresa = request.form['empresaId']
    empresa = request.form['Empresa'].upper()
    grupo = request.form['Grupo']
    atividade = request.form['Atividade']
    folha = request.form['Folha']
    email = request.form['Email'].lower()  # Convert email to lowercase
    # Default to an empty string if not provided
    marcar = request.form.get('Marcar', '')

    # Update the database with optional Marcar
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute(
        "UPDATE empresas SET Empresa=?, Grupo=?, Atividade=?, Folha=?, Email=?, Marcar=?, Log_alteracao=? WHERE rowid=?",
        (empresa, grupo, atividade, folha, email, marcar, log_alteracao, id_empresa)
    )
    conexao.commit()
    conexao.close()

    # Reload the updated list of companies
    empresas = atualizar_treeview_empresa()
    return render_template('cadastro_empresas.html', empresas=empresas, lista_folha=lista_folha_cadastro_emp, lista_grupo=lista_Grupo_cadastro_empresa, lista_atividade=lista_atividade_cadastro_emp)


@app.route('/excluir_empresa/<int:id_empresa>')
def excluir_empresa(id_empresa):
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute("DELETE FROM empresas WHERE rowid=?", (id_empresa,))
    conexao.commit()
    conexao.close()

    empresas = atualizar_treeview_empresa()
    return render_template('cadastro_empresas.html', empresas=empresas, lista_folha=lista_folha_cadastro_emp, lista_grupo=lista_Grupo_cadastro_empresa, lista_atividade=lista_atividade_cadastro_emp)

# ------------------------------------------------------------------------
#                               CADASTRO PESSOAS
# ------------------------------------------------------------------------


def atualizar_treeview_pessoa():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar as pessoas.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    # Conecta ao banco de dados
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    # Seleciona todas as pessoas do banco de dados
    c.execute("SELECT rowid, * FROM pessoas WHERE Id_user = ?",
              (usuario_autenticado,))

    pessoas = c.fetchall()  # Obtém todas as linhas da consulta
    conexao.close()  # Fecha a conexão com o banco de dados
    return pessoas  # Retorna a lista de pessoas


# GET é usado para obter recursos do servidor
@app.route('/cadastro_pessoas', methods=['GET'])
def exibir_formulario_cadastro_pessoas():
    if USUARIO_AUTENTICADO:
        pessoas = atualizar_treeview_pessoa()
        return render_template('cadastro_pessoas.html', pessoas=pessoas,
                               lista_empresa=lista_empresas()
                               )
    else:
        return redirect(url_for('index'))


# POST é usado para enviar dados para o servidor
@app.route('/cadastro_pessoas', methods=['POST'])
def cadastro_pessoas():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        if 'usuario' not in session:
            flash('Você precisa estar autenticado para realizar essa operação.', 'error')
            return redirect(url_for('index'))

        # Obtém o usuário autenticado da sessão
        usuario_autenticado = session['usuario']

        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        c.execute("INSERT INTO pessoas VALUES (:Pessoa,:Telefone,:Empresa,:Marcar,:Log_alteracao,:Id_user)",
                  {
                      'Pessoa': request.form['Pessoa'].title(),
                      'Telefone': request.form['Telefone'],
                      'Empresa': request.form['Empresa'],
                      'Marcar': request.form['Marcar'],
                      'Log_alteracao': log_alteracao,
                      'Id_user': usuario_autenticado
                  })
        conexao.commit()
        conexao.close()

        pessoas = atualizar_treeview_pessoa()
        return render_template('cadastro_pessoas.html', pessoas=pessoas, lista_empresa=lista_empresas())


@app.route('/editar_pessoa', methods=['POST'])
def editar_pessoa():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Use .get() to allow Marcar to be optional
    id_pessoa = request.form['pessoaId']
    pessoa = request.form['Pessoa'].title()
    telefone = request.form['Telefone']
    empresa = request.form['Empresa']
    # Default to an empty string if not provided
    marcar = request.form.get('Marcar', '')

    # Update the database with optional Marcar
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute(
        "UPDATE pessoas SET Pessoa=?, Telefone=?, Empresa=?, Marcar=?, Log_alteracao=? WHERE rowid=?",
        (pessoa, telefone, empresa, marcar, log_alteracao, id_pessoa)
    )
    conexao.commit()
    conexao.close()

    # Reload the updated list of companies
    pessoas = atualizar_treeview_pessoa()
    return render_template('cadastro_pessoas.html', pessoas=pessoas, lista_empresa=lista_empresas())


@app.route('/excluir_pessoa/<int:id_pessoa>')
def excluir_pessoa(id_pessoa):
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute("DELETE FROM pessoas WHERE rowid=?", (id_pessoa,))
    conexao.commit()
    conexao.close()

    pessoas = atualizar_treeview_pessoa()
    return render_template('cadastro_pessoas.html', pessoas=pessoas, lista_empresa=lista_empresas())


# ------------------------------------------------------------------------
#                               CADASTRO CONFIGURAÇÕES
# ------------------------------------------------------------------------

# Função para obter dados da tabela configuracoes (única linha)
def atualizar_configuracoes():
    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os dados.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute("SELECT * FROM configuracoes WHERE Id_user = ? LIMIT 1",
              (usuario_autenticado,))  # Seleciona a única configuração
    configuracoes = c.fetchall()
    conexao.close()
    return configuracoes


@app.route('/cadastro_configuracoes', methods=['GET'])
def exibir_formulario_configuracoes():
    if USUARIO_AUTENTICADO:
        configuracoes = atualizar_configuracoes()
        if configuracoes:
            configuracao = configuracoes[0]
            return render_template('configuracoes.html', configuracao=configuracao)
        else:
            return render_template('configuracoes.html')
    else:
        return redirect(url_for('index'))

# POST para salvar ou editar configurações


@app.route('/configuracoes', methods=['POST'])
def salvar_configuracoes():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        servidor_smtp = request.form['servidor_smtp']
        servidor_imap = request.form['servidor_imap']
        porta_smtp = request.form['porta_smtp']
        remetente_email = request.form['remetente_email'].lower()
        senha = request.form['senha']
        caminho_assinatura = request.form['caminho_assinatura']
        intervalo_busca = request.form['intervalo_busca']
        log_alteracao = log_alteracao

        if 'usuario' not in session:
            flash('Você precisa estar autenticado para realizar essa operação.', 'error')
            return redirect(url_for('index'))

        # Obtém o usuário autenticado da sessão
        usuario_autenticado = session['usuario']

        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        # Inserir ou atualizar a configuração única
        c.execute("""
            INSERT OR REPLACE INTO configuracoes (rowid, servidor_smtp, servidor_imap, porta_smtp, remetente_email, senha, caminho_assinatura, intervalo_busca, log_alteracao, Id_user)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (servidor_smtp, servidor_imap, porta_smtp, remetente_email, senha, caminho_assinatura, intervalo_busca, log_alteracao, usuario_autenticado))
        conexao.commit()
        conexao.close()

        configuracoes = atualizar_configuracoes()
        return render_template('configuracoes.html', configuracoes=configuracoes)

# Função para excluir configuração


@app.route('/excluir_configuracao', methods=['POST'])
def excluir_configuracao():
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    # Exclui a configuração existente (única)
    c.execute("DELETE FROM configuracoes WHERE rowid = 1")
    conexao.commit()
    conexao.close()

    configuracoes = atualizar_configuracoes()
    return render_template('configuracoes.html', configuracoes=configuracoes)

# ------------------------------------------------------------------------
#                               CADASTRO CAMINHO ANEXOS
# ------------------------------------------------------------------------


def atualizar_treeview_anexos_email():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os anexos.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    # Conecta ao banco de dados
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    # Seleciona todos os anexos de email do banco de dados
    c.execute("SELECT rowid, * FROM anexos_email WHERE Id_user = ?",
              (usuario_autenticado,))
    anexos = c.fetchall()  # Obtém todas as linhas da consulta
    conexao.close()  # Fecha a conexão com o banco de dados
    return anexos  # Retorna a lista de anexos


@app.route('/cadastro_anexos_email', methods=['GET'])
def exibir_formulario_cadastro_anexos_email():
    if USUARIO_AUTENTICADO:
        anexos = atualizar_treeview_anexos_email()
        return render_template('cadastro_anexos_email.html', anexos=anexos,
                               lista_empresas=lista_empresas(),
                               lista_assunto=Lista_assunto(),
                               lista_tipo_anexo=lista_tipo_anexo)
    else:
        return redirect(url_for('index'))


@app.route('/cadastro_anexos_email', methods=['POST'])
def cadastro_anexos_email():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        if 'usuario' not in session:
            flash('Você precisa estar autenticado para realizar essa operação.', 'error')
            return redirect(url_for('index'))

        # Obtém o usuário autenticado da sessão
        usuario_autenticado = session['usuario']

        conexao = sqlite3.connect('cadastro.db')
        c = conexao.cursor()
        c.execute("INSERT INTO anexos_email (Empresa, Caminho_anexo, Expressao_anexo, Assunto, Tipo, Log_alteracao, Id_user) VALUES (:Empresa, :Caminho_anexo, :Expressao_anexo, :Assunto, :Tipo, :Log_alteracao, :Id_user)",
                  {
                      'Empresa': request.form['Empresa'].upper(),
                      'Caminho_anexo': request.form['Caminho_anexo'].replace('\\', '/'),
                      'Expressao_anexo': '',
                      'Assunto': request.form['Assunto'],
                      'Tipo': request.form['Tipo'],
                      'Log_alteracao': log_alteracao,
                      'Id_user': usuario_autenticado
                  })
        conexao.commit()
        conexao.close()

        anexos = atualizar_treeview_anexos_email()
        return render_template('cadastro_anexos_email.html', anexos=anexos, lista_empresas=lista_empresas(), lista_assunto=Lista_assunto())


@app.route('/editar_anexo_email', methods=['POST'])
def editar_anexo_email():
    log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    id_anexo = request.form['anexoId']
    empresa = request.form['Empresa'].upper()
    caminho_anexo = request.form['Caminho_anexo'].replace('\\', '/')
    expressao_anexo = ''
    assunto = request.form['Assunto']
    tipo = request.form['Tipo']
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute(
        "UPDATE anexos_email SET Empresa=?, Caminho_anexo=?, Expressao_anexo=?, Assunto=?, Tipo=?, Log_alteracao=? WHERE rowid=?",
        (empresa, caminho_anexo, expressao_anexo, assunto, tipo, log_alteracao, id_anexo)
    )
    conexao.commit()
    conexao.close()

    anexos = atualizar_treeview_anexos_email()
    return render_template('cadastro_anexos_email.html', anexos=anexos)


@app.route('/excluir_anexo_email/<int:id_anexo>')
def excluir_anexo_email(id_anexo):
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()
    c.execute("DELETE FROM anexos_email WHERE rowid=?", (id_anexo,))
    conexao.commit()
    conexao.close()

    anexos = atualizar_treeview_anexos_email()
    return render_template('cadastro_anexos_email.html', anexos=anexos)
# ----------------------------------------------------------------------------
#                            VISUALIZAR ANEXOS
# ----------------------------------------------------------------------------
# Função para conectar ao banco de dados e buscar os anexos


def get_anexos():
    # Conectar ao banco de dados SQLite (substitua o caminho para o seu banco de dados)
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()

    # Query SQL para buscar os dados

    cursor.execute('SELECT * FROM anexos_email_temp')

    # Inner join, para demonstrar apenas os anexos das empresas filtradas..
    query = '''
    SELECT 
        *
    FROM anexos_email_temp ae
    INNER JOIN dados_enviar de ON ae.Empresa = de.Empresa
    '''
    cursor.execute(query)
    anexos = cursor.fetchall()  # Retorna todos os resultados

    conn.close()  # Fechar a conexão com o banco de dados
    return anexos
# /visualizar_anexos


@app.route('/visualizar_anexos')
def visualizar_anexos():
    anexos = get_anexos()  # Chama a função que retorna os dados
    return render_template('visualizar_anexos.html', anexos=anexos)


#----------------------------------------------------------------------------
#                            VISUALIZAR DESTINATÁRIOS
#----------------------------------------------------------------------------
# Função para buscar os destinatários do banco de dados
def get_destinatarios():
    conn = sqlite3.connect('cadastro.db')
    cursor = conn.cursor()
    
    # Query para buscar os campos específicos da tabela dados_enviar
    query = '''
    SELECT 
        Pessoa, Telefone, Empresa, Assunto
    FROM dados_enviar
    '''
    cursor.execute(query)
    destinatarios = cursor.fetchall()  # Retorna todos os resultados

    conn.close()
    return destinatarios

# Rota para renderizar a página de visualização de destinatários
@app.route('/visualizar_destinatarios')
def visualizar_destinatarios():
    destinatarios = get_destinatarios()  # Chama a função que busca os dados
    return render_template('visualizar_destinatarios.html', destinatarios=destinatarios)


@app.route('/confirmar_envio_msg')
def confirmar_envio_msg():
    enviar_mensagens_whatsapp()  # Chama a função que envia os e-mails (ESSA FUNÇÃO QUE ESTAVA ATIVA)
    # Redireciona para a página de anexos novamente
    return redirect(url_for('visualizar_destinatarios'))
#-----------------------------------------------------------------------------
#                          CHECAR STATUS DE LOG NO QRCODE
#-----------------------------------------------------------------------------
@app.route('/check_status')
def check_status():
    status_path = os.path.join(app.static_folder, 'status.json')
    status_data = {'logado': False, 'data': 'N/A'}
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    except Exception as e:
        print(f"Não foi possível ler o status: {e}")
        
    return jsonify(status_data)

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True, use_reloader=False)
