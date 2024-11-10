# routes/routes.py

from flask import Blueprint, request, jsonify
from app.models import Usuario  # Importa o modelo Usuario
from app.app import db  # Importa o objeto db

# Cria o blueprint para as rotas de usuários
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
