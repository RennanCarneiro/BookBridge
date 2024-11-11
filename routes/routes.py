# routes/routes.py

from flask import Blueprint, request, jsonify
from app.models import Usuario, Clube  # Importa os modelos Usuario e Clube
from app.app import db  # Importa o objeto db

# Blueprint para as rotas de usuários
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['POST'])
def create_usuario():
    """Rota para criar um novo usuário."""
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'message': 'Dados incompletos'}), 400

    usuario = Usuario(nome=nome, email=email)
    usuario.set_password(senha)

    try:
        db.session.add(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuário criado com sucesso!'}), 201
    except Exception as e:
        db.session.rollback()
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
        return jsonify({'message': 'Usuário não encontrado'}), 404

    usuario.nome = data.get('nome', usuario.nome)
    usuario.email = data.get('email', usuario.email)
    senha = data.get('senha')
    if senha:
        usuario.set_password(senha)

    try:
        db.session.commit()
        return jsonify({'message': 'Usuário atualizado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    """Rota para deletar um usuário."""
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({'message': 'Usuário não encontrado'}), 404

    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'message': 'Usuário deletado com sucesso!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


# Blueprint para as rotas de clubes
clubes_bp = Blueprint('clubes', __name__)

@clubes_bp.route('/clubes', methods=['POST'])
def create_clube():
    """Rota para criar um novo clube."""
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    id_usuario_criador = data.get('id_usuario_criador')

    if not nome or not id_usuario_criador:
        return jsonify({'message': 'Dados incompletos'}), 400

    clube = Clube(nome=nome, descricao=descricao, id_usuario_criador=id_usuario_criador)

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
