from app import db #improtando objeto db que representa o banco de dados
from werkzeug.security import generate_password_hash, check_password_hash #importando funções para gerar/verificar senhas

#definir modelo de dados usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios' #definindo nome da tabela
    id = db.column(db.Integer, primary_key=True) #definindo a coluna id como chave primaria
    nome = db.column(db.String(50), nullable=False) #definindo a coluna nome
    email = db.Column(db.String(100), unique=True, nullable=False) #definindo a coluna email
    senha_hash = db.Column(db.String(128), nullable=False) #definindo uma string para armazenar o hash da senha
    clubes = db.relationship('Clube', backref='criador', lazy=True) #definindo relacionamento clube

    #função para definir a senha do usuario
    def set_password(self,senha):
        # Recebe uma senha gera um hash e armazena no campo senha_hash
        self.senha_hash = generate_password_hash(senha)

    #função para verificar se a senha é valida
    def check_password(self,senha):
        # compara a senha fornecida com o hash armazenado e retorna true caso coincidam
        return check_password_hash(self.senha_hash, senha)

    #metodo para debug, define o obj como string
    def __repr__(self):
        return f"<Usuario {self.nome}>"

class Clube(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    #chave estrangeira que faz referencia a usuario que criou o clube
    id_usuario_criador = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def __repr__(self):
        return f"<Clube {self.nome}>"