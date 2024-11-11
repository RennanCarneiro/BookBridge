# app/models.py

from app.database import db  # Importa o objeto db que representa o banco de dados
from werkzeug.security import generate_password_hash, check_password_hash  # Importa funções para gerar/verificar senhas


# Definir modelo de dados Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Define o nome da tabela

    id = db.Column(db.Integer, primary_key=True)  # Define a coluna id como chave primária
    nome = db.Column(db.String(50), nullable=False)  # Define a coluna nome
    email = db.Column(db.String(100), unique=True, nullable=False)  # Define a coluna email
    senha_hash = db.Column(db.String(512), nullable=False)  # Define uma string para armazenar o hash da senha
    clubes = db.relationship('Clube', backref='criador', lazy=True)  # Define relacionamento com Clube

    # Função para definir a senha do usuário
    def set_password(self, senha):
        # Recebe uma senha, gera um hash e armazena no campo senha_hash
        self.senha_hash = generate_password_hash(senha)

    # Função para verificar se a senha é válida
    def check_password(self, senha):
        # Compara a senha fornecida com o hash armazenado e retorna True se coincidirem
        return check_password_hash(self.senha_hash, senha)

    # Método para representar o objeto como string
    def __repr__(self):
        return f"<Usuario {self.nome}>"


# Definir modelo de dados Clube
class Clube(db.Model):
    __tablename__ = 'clubes'  # Define o nome da tabela

    id = db.Column(db.Integer, primary_key=True)  # Define a coluna id como chave primária
    nome = db.Column(db.String(100), nullable=False)  # Define a coluna nome
    descricao = db.Column(db.String(255), nullable=True)  # Define a coluna descrição
    id_usuario_criador = db.Column(db.Integer, db.ForeignKey('usuarios.id'),
                                   nullable=False)  # Chave estrangeira para o criador

    # Método para representar o objeto como string
    def __repr__(self):
        return f"<Clube {self.nome}>"

class Livro(db.Model):
    __tablename__ = 'livros' # nome da tabela

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    id_clube = db.Column(db.Integer, db.ForeignKey('clubes.id'), nullable=False)

    def __repr__(self):
        return f"<Livro {self.titulo} por {self.autor}>"

class Avaliacao(db.Model):
    __tablename__ = 'avaliacoes'

    id = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(255), nullable=True)
    nota = db.Column(db.Integer, nullable=False)  # Exemplo de escala: 1 a 5
    id_livro = db.Column(db.Integer, db.ForeignKey('livros.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return f"<Avaliacao {self.nota} para o Livro {self.id_livro}>"