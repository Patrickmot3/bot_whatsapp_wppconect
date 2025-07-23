import requests

# Nova URL do servidor Node.js hospedado no Render
WHATSAPP_API_URL = "https://bot-whatsapp-wppconect-1.onrender.com/enviar"

def gerar_qrcode():
    """
    Função de informação — o QR code é gerado ao acessar o endpoint ou iniciar o servidor Node.js.
    """
    print("ℹ️  Certifique-se de que o servidor Node.js na Render está em execução.")
    print("URL do servidor:", WHATSAPP_API_URL.replace("/enviar", ""))

def enviar_mensagens_whatsapp():
    """
    Envia uma requisição HTTP POST para o servidor Node.js publicado na Render.
    """
    try:
        response = requests.post(WHATSAPP_API_URL)

        if response.status_code == 200:
            print("✅ Requisição enviada com sucesso para o servidor Node.js.")
            print("Resposta:", response.json())
        else:
            print("❌ Erro ao enviar requisição para o servidor Node.js.")
            print("Status:", response.status_code)
            print("Resposta:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao conectar com o servidor Node.js: {e}")
