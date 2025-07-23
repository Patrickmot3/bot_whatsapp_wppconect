import os
from datetime import datetime, timedelta
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Caminho para o banco de dados SQLite


def buscar_anexos():

    # Verifica se o usuário está autenticado
    if 'usuario' not in session:
        flash('Você precisa estar autenticado para acessar os dados.', 'error')
        return []

    # Obtém o nome do usuário autenticado
    usuario_autenticado = session['usuario']

    # Conectar ao banco de dados
    conexao = sqlite3.connect('cadastro.db')
    c = conexao.cursor()

    # Obter intervalo de busca
    c.execute("SELECT intervalo_busca FROM configuracoes WHERE Id_user = ? ORDER BY oid DESC LIMIT 1",
              (usuario_autenticado,))
    intervalo_busca_tmp = c.fetchone()[0]  # Pega o valor do campo 'Assunto'
    intervalo_busca = int(intervalo_busca_tmp)

    # Criando uma VARIAVEL com o campo ASSUNTO
    c.execute("SELECT Assunto FROM dados_tela_envio WHERE Id_user = ? ORDER BY oid DESC LIMIT 1",
              (usuario_autenticado,))
    ultimo_assunto_input = c.fetchone()[0]  # Pega o valor do campo 'Assunto'

    db_path = 'cadastro.db'  # Substitua pelo caminho correto do seu banco

    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Definir a data limite (10 dias atrás)
    data_limite = datetime.now() - timedelta(days=intervalo_busca)

    # Limpar a tabela temporária
    cursor.execute('DELETE FROM anexos_email_temp')

    # Consulta com filtro no campo Assunto

    # query = '''
    # SELECT
    #     ae.Caminho_anexo,
    #     ae.Empresa,
    #     ae.Assunto
    # FROM anexos_email ae
    # INNER JOIN dados_enviar de ON ae.Empresa = de.Empresa
    # WHERE ae.Assunto = ? AND ae.Id_user = ?
    # '''
    query = 'SELECT Caminho_anexo, Empresa, Assunto, Tipo FROM anexos_email WHERE Assunto = ? and Id_user = ?'
    cursor.execute(query, (ultimo_assunto_input, usuario_autenticado))
    resultados_a_ordenar = cursor.fetchall()

    # Ordena os resultados pela coluna "Empresa" (índice 1)
    resultados = sorted(resultados_a_ordenar, key=lambda x: x[1])

    if not resultados:
        print(
            f"Nenhum registro encontrado para o assunto: {ultimo_assunto_input}")
        conn.close()
        return

    for resultado in resultados:
        pasta = resultado[0]  # Caminho do anexo
        Nome_empresa = resultado[1]  # Nome da empresa
        Assunto = resultado[2]  # Assunto
        Tipo = resultado[3]  # Assunto

        # Verificar se a pasta existe
        if os.path.exists(pasta) and os.path.isdir(pasta):
            # print(f"Verificando arquivos na pasta: {pasta}")

            # Listar arquivos na pasta
            for nome_arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, nome_arquivo)

                # Verificar se é um arquivo
                if os.path.isfile(caminho_arquivo):
                    # Obter data de modificação
                    tempo_modificacao = os.path.getmtime(caminho_arquivo)
                    data_modificacao = datetime.fromtimestamp(
                        tempo_modificacao)

                    # Verificar se a data está dentro do intervalo
                    if data_modificacao >= data_limite:
                        # Formatar datas
                        data_modificacao_formatada = data_modificacao.strftime(
                            '%Y-%m-%d %H:%M:%S')
                        log_alteracao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        caminho_completo_anexo = os.path.join(
                            pasta, nome_arquivo)
                        # Obtém o nome do usuário autenticado
                        usuario_autenticado = session['usuario']

                        # Inserir dados na tabela temporária
                        cursor.execute('''
                            INSERT INTO anexos_email_temp (Empresa, Assunto, Caminho_pasta, Nome_anexo, Caminho_anexo, Tipo, Modificacao_anexo, Log_alteracao, Id_user)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (Nome_empresa, Assunto, pasta, nome_arquivo, caminho_completo_anexo, Tipo, data_modificacao_formatada, log_alteracao, usuario_autenticado))

                        # print(f'Arquivo: {nome_arquivo}, Data de Modificação: {data_modificacao_formatada}')
        else:
            print(f"A pasta '{pasta}' não existe ou não é válida.")

    # Salvar alterações e fechar conexão
    conn.commit()
    conn.close()

    print("✅ Busca de anexos concluída com sucesso (busca_arquivos.py)")
