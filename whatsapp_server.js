const fs = require('fs');
const path = require('path');
const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();

const app = express();
app.use(express.json());

let wppClient; // Variável para armazenar o cliente conectado

// 1. Inicia o cliente WPPConnect quando o servidor é iniciado
wppconnect
  .create({
    session: 'sessionName321',
    catchQR: (base64Qr, asciiQR) => {
      console.log('✅ QR Code Recebido. Salve a imagem e atualize o status.');
      const matches = base64Qr.match(/^data:([A-Za-z-+/]+);base64,(.+)$/);
      if (!matches || matches.length !== 3) {
        return;
      }
      const staticDir = path.join(__dirname, 'static');
      if (!fs.existsSync(staticDir)) {
        fs.mkdirSync(staticDir, { recursive: true });
      }

      try {
        const buffer = Buffer.from(matches[2], 'base64');
      
        const staticDir = path.join(__dirname, 'static');
        if (!fs.existsSync(staticDir)) {
          fs.mkdirSync(staticDir, { recursive: true });
        }
      
        const filePath = path.join(staticDir, 'out.png');
        fs.writeFileSync(filePath, buffer, 'binary');
        console.log('✅ QR Code salvo em:', filePath);
      
        const statusInfo = {
          logado: false,
          data: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })
        };
        fs.writeFileSync(path.join(staticDir, 'status.json'), JSON.stringify(statusInfo, null, 2));
      } catch (error) {
        console.error('❌ Erro ao salvar QR Code:', error);
      }
    },
    statusFind: (statusSession, session) => {
        console.log('Status da sessão: ', statusSession);
        const logado = statusSession === 'isLogged' || statusSession === 'qrReadSuccess' || statusSession === 'chatsAvailable';
         const statusInfo = {
            logado: logado,
            data: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })
          };
        fs.writeFileSync(path.join(__dirname, 'static', 'status.json'), JSON.stringify(statusInfo, null, 2));
    },
    logQR: false,
  })
  .then((client) => {
    wppClient = client; // Armazena o cliente na variável global
    console.log('✅ Cliente WPPConnect iniciado com sucesso!');
  })
  .catch((error) => console.log('❌ Erro ao iniciar cliente:', error));


// 2. Cria um endpoint para enviar mensagens
app.post('/enviar', (req, res) => {
  if (!wppClient) {
    return res.status(500).json({ error: 'Cliente WhatsApp não está pronto.' });
  }

  // Busca os contatos do banco de dados na hora do envio
  const db = new sqlite3.Database('cadastro.db');
  const sql = 'SELECT Pessoa, Telefone, Corpo, Caminhos_anexos FROM dados_enviar';

  db.all(sql, [], (err, rows) => {
    if (err) {
      db.close();
      return res.status(500).json({ error: 'Erro ao consultar o banco de dados.' });
    }
    
    // Envia as mensagens usando o cliente já conectado
    rows.forEach((contato, index) => {
      const telefone = '55' + contato.Telefone.toString().replace(/\D/g, '') + '@c.us';
      const mensagem = contato.Corpo.replace(/\\n/g, '\n');
      const caminhos = contato.Caminhos_anexos ? contato.Caminhos_anexos.replace(/\\/g, '/').split(',').map(c => c.trim()) : [];
      
      setTimeout(async () => {
        try {
          await wppClient.sendText(telefone, mensagem);
          console.log(`✅ Mensagem enviada para ${telefone}`);

          for (let caminho of caminhos) {
            if (fs.existsSync(caminho)) {
              await wppClient.sendFile(telefone, caminho);
              console.log(`📎 Anexo enviado para ${telefone}: ${caminho}`);
            }
          }
        } catch (erro) {
          console.error(`❌ Erro ao enviar para ${telefone}:`, erro);
        }
      }, index * 4000);
    });

    res.status(200).json({ success: 'Processo de envio iniciado.' });
    db.close();
  });
});

// 3. Servir arquivos estáticos (como QR code e status)
app.use('/static', express.static(path.join(__dirname, 'static')));

// 4. Inicia o servidor Express para ouvir as requisições do Flask
const PORT = 3000;
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8" />
      <title>QR Code WhatsApp</title>
    </head>
    <body style="text-align: center; font-family: sans-serif; margin-top: 50px;">
      <h1>QR Code para Conexão WhatsApp</h1>
      <img src="/static/out.png" alt="QR Code" style="width: 300px; border: 1px solid #ccc;" />
      <p>Status da Sessão: <a href="/static/status.json" target="_blank">Ver status</a></p>
      <p>Atualize a página se o QR expirar.</p>
    </body>
    </html>
  `);
});
app.listen(PORT, () => {
  console.log(`🚀 Servidor Node.js para WhatsApp rodando na porta ${PORT}`);
});