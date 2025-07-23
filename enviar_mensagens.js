const fs = require('fs');
const wppconnect = require('@wppconnect-team/wppconnect');
const sqlite3 = require('sqlite3').verbose();

// Função para buscar os contatos do banco SQLite
function buscarContatos(callback) {
  const db = new sqlite3.Database('cadastro.db', sqlite3.OPEN_READONLY, (err) => {
    if (err) {
      console.error('Erro ao abrir o banco:', err.message);
      return;
    }
  });

  const sql = 'SELECT Pessoa, Telefone, Corpo, Caminhos_anexos FROM dados_enviar';

  db.all(sql, [], (err, rows) => {
    if (err) {
      console.error('Erro ao consultar o banco:', err.message);
      callback([]);
    } else {
      callback(rows);
    }
    db.close();
  });
}

wppconnect
  .create({
    session: 'sessionTemp123', // A mesma sessão usada no gerarQR.js
    autoClose: false,       // Mantém o cliente aberto
  })
  .then((client) => start(client))
  .catch((error) => console.log('❌ Erro ao iniciar cliente:', error));

// Envia mensagens para os contatos do banco de dados
function start(client) {
  buscarContatos((contatos) => {
    contatos.forEach((contato, index) => {
      const telefone = '55' + contato.Telefone.toString().replace(/\D/g, '') + '@c.us';
      const mensagem = contato.Corpo.replace(/\\n/g, '\n');
      const caminhos = contato.Caminhos_anexos
        ? contato.Caminhos_anexos
            .replace(/\\/g, '/')
            .split(',')
            .map((c) => c.trim())
        : [];

      setTimeout(async () => {
        try {
          await client.sendText(telefone, mensagem);
          console.log(`✅ Mensagem enviada para ${telefone}`);

          for (let caminho of caminhos) {
            if (fs.existsSync(caminho)) {
              await client.sendFile(telefone, caminho);
              console.log(`📎 Anexo enviado para ${telefone}: ${caminho}`);
            } else {
              console.warn(`⚠️ Caminho não encontrado: ${caminho}`);
            }
          }
        } catch (erro) {
          console.error(`❌ Erro ao enviar para ${telefone}:`, erro);
        }
      }, index * 4000);
    });
  });
}
