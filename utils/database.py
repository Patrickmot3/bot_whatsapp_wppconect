import sqlite3
from datetime import datetime
import hashlib
from typing import Optional

class Database:
    def __init__(self, db_name: str = "cadastro.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    log_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def cadastrar_usuario(self, nome: str, usuario: str, senha: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                hashed_password = self.hash_password(senha)
                cursor.execute(
                    'INSERT INTO login (nome, usuario, senha, log_alteracao) VALUES (?, ?, ?, ?)',
                    (nome, usuario, hashed_password, datetime.now())
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def verificar_login(self, usuario: str, senha: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            hashed_password = self.hash_password(senha)
            cursor.execute(
                'SELECT * FROM login WHERE usuario = ? AND senha = ?',
                (usuario, hashed_password)
            )
            return cursor.fetchone() is not None

    def buscar_usuario(self, usuario: str) -> Optional[tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM login WHERE usuario = ?', (usuario,))
            return cursor.fetchone()