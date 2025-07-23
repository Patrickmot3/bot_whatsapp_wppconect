import subprocess
import requests # Importe a biblioteca

# URL do seu servidor Node.js
WHATSAPP_API_URL = "http://localhost:3000/enviar"

def gerar_qrcode():
    """
    Esta função agora deve apenas garantir que o servidor Node.js esteja rodando.
    Você deve iniciá-lo manualmente ou usar uma ferramenta como o 'concurrently' para
    iniciar o servidor Flask e o Node juntos.
    """
    print("ℹ️  Certifique-se de que o 'whatsapp_server.js' está em execução.")
    # Não é mais necessário executar o script 'gerarQR.js' daqui.
    # O servidor Node.js cuidará disso ao ser iniciado.
    # Exemplo: subprocess.Popen(['node', 'whatsapp_server.js'])
    # Mas a melhor prática é rodá-lo separadamente.

def enviar_mensagens_whatsapp():
    """
    Esta função agora envia uma requisição HTTP para o servidor Node.js.
    """
    try:
        # Apenas aciona o endpoint. O servidor Node buscará os dados do DB.
        response = requests.post(WHATSAPP_API_URL)
        
        if response.status_code == 200:
            print("✅ Requisição de envio enviada com sucesso para o servidor Node.js.")
            print("Resposta do servidor:", response.json())
        else:
            print("❌ Erro ao enviar requisição para o servidor Node.js.")
            print("Status:", response.status_code)
            print("Resposta:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao conectar com o servidor Node.js: {e}")