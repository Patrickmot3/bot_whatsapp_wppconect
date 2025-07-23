import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import smtplib
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# -----------------------------------------------------------------
#       Busca configurações do banco de dados
# -----------------------------------------------------------------
conexao = sqlite3.connect('cadastro.db')
c = conexao.cursor()
c.execute("SELECT servidor_smtp, Servidor_IMAP, porta_smtp, remetente_email, senha, caminho_assinatura FROM configuracoes LIMIT 1")
configuracao = c.fetchone()
conexao.close()
servidor_smtp = configuracao[0]
Servidor_IMAP = configuracao[1]
porta_smtp = configuracao[2]
remetente_email = configuracao[3]
senha = configuracao[4]
caminho_assinatura = configuracao[5]




def enviar_email():
    
    # Carregar os dados do arquivo Excel
    df = pd.read_excel('enviar_temp.xlsx')
    DadosParaEnvio = df[['Empresa', 'Emails',
                         'Caminhos_anexos', 'Assunto', 'Corpo']]

    def enviar_email_com_anexos(para, assunto, corpo, anexos_caminhos, imagem_caminho):

        print(f"Servidor SMTP: {servidor_smtp}, \n"
            f"Porta: {porta_smtp}, \n"
            f"Servidor_IMAP: {Servidor_IMAP}, \n"
            f"Caminho assinatura: {caminho_assinatura}")



        # Construir e-mail
        mensagem = MIMEMultipart()
        mensagem['From'] = remetente_email
        mensagem['To'] = ', '.join(para)
        mensagem['Subject'] = assunto

        # Corpo do e-mail em HTML
        corpo_html = f"""
        <html>
        <body>
            <p>{corpo.replace('\n', '<br>')}</p>
            <br><br>
            <p>Atenciosamente;<p>
            <img src="cid:assinatura_email">
        </body>
        </html>
        """
        mensagem.attach(MIMEText(corpo_html, 'html'))

        # Adicionar anexos
        for anexo_caminho in anexos_caminhos.split(','):
            anexo_caminho = anexo_caminho.strip()
            if anexo_caminho:
                try:
                    with open(anexo_caminho, "rb") as anexo:
                        anexo_mime = MIMEApplication(anexo.read())
                        anexo_mime.add_header(
                            'Content-Disposition', 'attachment', filename=anexo_caminho.split('\\')[-1])
                        mensagem.attach(anexo_mime)
                except FileNotFoundError:
                    print(f"Arquivo não encontrado: {anexo_caminho}")

        # Adicionar imagem de assinatura
        with open(imagem_caminho, "rb") as img:
            img_mime = MIMEImage(img.read())
            img_mime.add_header('Content-ID', '<assinatura_email>')
            img_mime.add_header('Content-Disposition',
                                'inline', filename="assinatura.png")
            mensagem.attach(img_mime)

        # Conectar ao servidor SMTP e enviar e-mail
        try:
            with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
                servidor.starttls()
                servidor.login(remetente_email, senha)
                servidor.send_message(mensagem)
                print(f"E-mail enviado com sucesso para {para}!")
        except smtplib.SMTPAuthenticationError:
            print("Erro de autenticação: verifique seu e-mail e senha.")
        except smtplib.SMTPConnectError:
            print("Erro de conexão: não foi possível conectar ao servidor SMTP.")
        except Exception as e:
            print("Erro ao enviar e-mail:", str(e))

    today = datetime.now()
    primeiro_dia_do_mes_atual = today.replace(day=1)
    mes_anterior = primeiro_dia_do_mes_atual - timedelta(days=1)

    # Formata os resultados
    mes_atual = today.strftime('%m/%Y')            # Mês e ano atual
    mes_anterior = mes_anterior.strftime('%m/%Y')  # Mês e ano anterior
    ano_atual = today.strftime('%Y')               # Ano atual
    ano_anterior = today.replace(
        year=today.year - 1).strftime('%Y')  # Ano anterior

    # Função para substituir os marcadores de data e empresa no texto
    def substituir_marcadores(texto, mes_atual, mes_anterior, ano_atual, ano_anterior, empresa):
        return (texto.replace("mes_ant_", mes_anterior)
                .replace("mes_", mes_atual)
                .replace("ano_", ano_atual)
                .replace("ano_ant_", ano_anterior)
                .replace("emp_", empresa)
                .replace("\\n", "\n"))

    # Enviar e-mails
    for _, linha in DadosParaEnvio.iterrows():
        destinatarios = [email.strip()
                         for email in linha['Emails'].split(',') if email.strip()]

        # Substituir marcadores de texto
        assunto_email = substituir_marcadores(
            linha['Assunto'], mes_atual, mes_anterior, ano_atual, ano_anterior, linha['Empresa'])
        corpo_email = substituir_marcadores(
            linha['Corpo'], mes_atual, mes_anterior, ano_atual, ano_anterior, linha['Empresa'])

        anexos_caminhos = linha['Caminhos_anexos']
        imagem_caminho = caminho_assinatura

        enviar_email_com_anexos(
            destinatarios, assunto_email, corpo_email, anexos_caminhos, imagem_caminho)
