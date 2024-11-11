# routes/routes.py
from functools import wraps
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app

from app.app import logger
from app.models import Usuario, Clube, Livro, Avaliacao  # Importa os modelos Usuario e Clube
from app.database import db  # Importa o objeto db


def gerador_token(user_id):
    # gera um token valido por 1 hora

    payload = {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=1)}  # expiração de uma hora para o token
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    logger.info(f'Token gerado para user_id: {user_id}')
    return token


# Blueprint para as rotas de usuários
usuarios_bp = Blueprint('usuarios', __name__)
auth_bp = Blueprint('auth', __name__)
livros_bp = Blueprint('Livros', __name__)
avaliacoes_bp = Blueprint('avaliacoes', __name__)
stats_bp = Blueprint('stats', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Rota de login para autenticar o usuário e fornecer um token JWT."""
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    # Verifica se o usuário existe e se a senha está correta
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.check_password(senha):
        # Gera um token JWT
        token = gerador_token(usuario.id)
        logger.info(f'Usuário {usuario.email} autenticado com sucesso.')
        return jsonify({'token': token}), 200

    # Se as credenciais forem inválidas
    logger.warning(f'Tentativa de login com falha para o email: {email}')
    return jsonify({'message': 'Credenciais inválidas'}), 401


# verificar se o token é valido


def requisicao_token(f):
    @wraps(f)  # Isso preserva o nome e a docstring originais da função
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logger.warning('Tentativa de acesso sem token de autenticação.')
            return jsonify({'message': 'Token é necessário'}), 401

        try:
            token = token.split(" ")[1]  # Token está no formato "Bearer <token>"
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(payload['user_id'])
            logger.info(f'Acesso autorizado para user_id: {current_user.id}')
        except jwt.ExpiredSignatureError:
            logger.warning('Token expirado')
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            logger.error('Token inválido')
            return jsonify({'message': 'Token inválido'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@usuarios_bp.route('/usuarios', methods=['POST'])
def create_usuario():
    """Rota para criar um novo usuário."""
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        logger.warning('Tentativa de criação de usuário com dados incompletos.')
        return jsonify({'message': 'Dados incompletos'}), 400

    usuario = Usuario(nome=nome, email=email)
    usuario.set_password(senha)

    try:
        db.session.add(usuario)
        db.session.commit()
        logger.info(f'Usuário criado com sucesso: {nome} (ID: {usuario.id})')
        return jsonify({'message': 'Usuário criado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao criar usuário: {e}')
        return jsonify({'message': str(e)}), 500


@usuarios_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
    """Rota para listar todos os usuários."""
    usuarios = Usuario.query.all()
    return jsonify([{'id': u.id, 'nome': u.nome, 'email': u.email} for u in usuarios])


@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    """Rota para atualizar um usuário existente."""
    data = request.get_json()
    usuario = Usuario.query.get(id)

    if not usuario:
        logger.warning(f'Tentativa de atualização de usuário não encontrado: ID {id}')
        return jsonify({'message': 'Usuário não encontrado'}), 404

    usuario.nome = data.get('nome', usuario.nome)
    usuario.email = data.get('email', usuario.email)
    senha = data.get('senha')
    if senha:
        usuario.set_password(senha)

    try:
        db.session.commit()
        logger.info(f'Usuário atualizado com sucesso: {usuario.nome} (ID: {usuario.id})')
        return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao atualizar usuário: {e}')
        return jsonify({'message': str(e)}), 500


@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    """Rota para deletar um usuário."""
    usuario = Usuario.query.get(id)

    if not usuario:
        logger.warning(f'Tentativa de deleção de usuário não encontrado: ID {id}')
        return jsonify({'message': 'Usuário não encontrado'}), 404

    try:
        db.session.delete(usuario)
        db.session.commit()
        logger.info(f'Usuário deletado com sucesso: {usuario.nome} (ID: {usuario.id})')
        return jsonify({'message': 'Usuário deletado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao deletar usuário: {e}')
        return jsonify({'message': str(e)}), 500


# Blueprint para as rotas de clubes
clubes_bp = Blueprint('clubes', __name__)


@clubes_bp.route('/clubes', methods=['POST'])
@requisicao_token
def create_clube(current_user):
    """Rota para criar um novo clube."""
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    # id_usuario_criador = data.get('id_usuario_criador')

    if not nome: #or not id_usuario_criador:
        return jsonify({'message': 'Dados incompletos'}), 400

    clube = Clube(nome=nome, descricao=descricao, id_usuario_criador=current_user.id) #id_usuario_criador

    try:
        db.session.add(clube)
        db.session.commit()
        return jsonify({'message': 'Clube criado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@clubes_bp.route('/clubes', methods=['GET'])
def get_clubes():
    """Rota para listar todos os clubes."""
    clubes = Clube.query.all()
    return jsonify([{'id': c.id, 'nome': c.nome, 'descricao': c.descricao} for c in clubes])


@clubes_bp.route('/clubes/<int:id>', methods=['PUT'])
@requisicao_token
def update_clube(id):
    """Rota para atualizar um clube existente."""
    data = request.get_json()
    clube = Clube.query.get(id)

    if not clube:
        return jsonify({'message': 'Clube não encontrado'}), 404

    clube.nome = data.get('nome', clube.nome)
    clube.descricao = data.get('descricao', clube.descricao)

    try:
        db.session.commit()
        return jsonify({'message': 'Clube atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@clubes_bp.route('/clubes/<int:id>', methods=['DELETE'])
@requisicao_token
def delete_clube(id):
    """Rota para deletar um clube."""
    clube = Clube.query.get(id)

    if not clube:
        return jsonify({'message': 'Clube não encontrado'}), 404

    try:
        db.session.delete(clube)
        db.session.commit()
        return jsonify({'message': 'Clube deletado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

#criar livros
@livros_bp.route('/clubes/<int:clube_id>/livros', methods=['POST'])
@requisicao_token
def create_livro(current_user, clube_id):
    """Rota para adicionar um novo livro a um clube."""
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')

    if not titulo or not autor:
        return jsonify({'message': 'Dados incompletos'}), 400

    clube = Clube.query.get(clube_id)
    if not clube or clube.id_usuario_criador != current_user.id:
        return jsonify({'message': 'Clube não encontrado ou acesso negado'}), 404

    livro = Livro(titulo=titulo, autor=autor, id_clube=clube_id)

    try:
        db.session.add(livro)
        db.session.commit()
        return jsonify({'message': 'Livro adicionado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

#listar livros
@livros_bp.route('/clubes/<int:clube_id>/livros', methods=['GET'])
@requisicao_token
def get_livros(current_user, clube_id):
    """Rota para listar todos os livros de um clube."""
    clube = Clube.query.get(clube_id)
    if not clube or clube.id_usuario_criador != current_user.id:
        return jsonify({'message': 'Clube não encontrado ou acesso negado'}), 404

    livros = Livro.query.filter_by(id_clube=clube_id).all()
    return jsonify([{'id': livro.id, 'titulo': livro.titulo, 'autor': livro.autor} for livro in livros])

#Atualizar livros
@livros_bp.route('/livros/<int:livro_id>', methods=['PUT'])
@requisicao_token
def update_livro(current_user, livro_id):
    """Rota para atualizar as informações de um livro."""
    data = request.get_json()
    livro = Livro.query.get(livro_id)

    if not livro:
        return jsonify({'message': 'Livro não encontrado'}), 404

    clube = Clube.query.get(livro.id_clube)
    if clube.id_usuario_criador != current_user.id:
        return jsonify({'message': 'Acesso negado'}), 403

    livro.titulo = data.get('titulo', livro.titulo)
    livro.autor = data.get('autor', livro.autor)

    try:
        db.session.commit()
        return jsonify({'message': 'Livro atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

#deletar livro(s)
@livros_bp.route('/livros/<int:livro_id>', methods=['DELETE'])
@requisicao_token
def delete_livro(current_user, livro_id):
    """Rota para deletar um livro."""
    livro = Livro.query.get(livro_id)

    if not livro:
        return jsonify({'message': 'Livro não encontrado'}), 404

    clube = Clube.query.get(livro.id_clube)
    if clube.id_usuario_criador != current_user.id:
        return jsonify({'message': 'Acesso negado'}), 403

    try:
        db.session.delete(livro)
        db.session.commit()
        return jsonify({'message': 'Livro deletado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@avaliacoes_bp.route('/livros/<int:livro_id>/avaliacoes', methods=['POST'])
@requisicao_token
def create_avaliacao(current_user, livro_id):
    """Rota para criar uma nova avaliação para um livro."""
    data = request.get_json()
    comentario = data.get('comentario')
    nota = data.get('nota')

    if not nota or not isinstance(nota, int) or not (1 <= nota <= 5):
        return jsonify({'message': 'Nota inválida, deve ser um número entre 1 e 5'}), 400

    livro = Livro.query.get(livro_id)
    if not livro:
        return jsonify({'message': 'Livro não encontrado'}), 404

    avaliacao = Avaliacao(comentario=comentario, nota=nota, id_livro=livro_id, id_usuario=current_user.id)

    try:
        db.session.add(avaliacao)
        db.session.commit()
        return jsonify({'message': 'Avaliação criada com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@avaliacoes_bp.route('/livros/<int:livro_id>/avaliacoes', methods=['GET'])
def get_avaliacoes(livro_id):
    """Rota para listar todas as avaliações de um livro."""
    livro = Livro.query.get(livro_id)
    if not livro:
        return jsonify({'message': 'Livro não encontrado'}), 404

    avaliacoes = Avaliacao.query.filter_by(id_livro=livro_id).all()
    return jsonify([
        {'id': avaliacao.id, 'comentario': avaliacao.comentario, 'nota': avaliacao.nota, 'id_usuario': avaliacao.id_usuario}
        for avaliacao in avaliacoes
    ])

@avaliacoes_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['PUT'])
@requisicao_token
def update_avaliacao(current_user, avaliacao_id):
    """Rota para atualizar uma avaliação existente."""
    data = request.get_json()
    avaliacao = Avaliacao.query.get(avaliacao_id)

    if not avaliacao or avaliacao.id_usuario != current_user.id:
        return jsonify({'message': 'Avaliação não encontrada ou acesso negado'}), 404

    avaliacao.comentario = data.get('comentario', avaliacao.comentario)
    avaliacao.nota = data.get('nota', avaliacao.nota)

    try:
        db.session.commit()
        return jsonify({'message': 'Avaliação atualizada com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@avaliacoes_bp.route('/avaliacoes/<int:avaliacao_id>', methods=['DELETE'])
@requisicao_token
def delete_avaliacao(current_user, avaliacao_id):
    """Rota para deletar uma avaliação."""
    avaliacao = Avaliacao.query.get(avaliacao_id)

    if not avaliacao or avaliacao.id_usuario != current_user.id:
        return jsonify({'message': 'Avaliação não encontrada ou acesso negado'}), 404

    try:
        db.session.delete(avaliacao)
        db.session.commit()
        return jsonify({'message': 'Avaliação deletada com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500