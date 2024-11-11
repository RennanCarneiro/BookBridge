# app/app.py
import os
from flask import Flask  # Importando a biblioteca Flask
from app.database import db
from flask_migrate import Migrate

# Inicializando o banco de dados e o sistema de migração
migrate = Migrate()


def create_app():
    app = Flask(__name__)  # Instanciando a aplicação Flask

    # Configurações da aplicação e do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:senha@localhost/bookbridge'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #definindo uma chave secreta
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'chave_secreta'

    # Inicializando o banco de dados e o sistema de migração com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)

    # Importando e registrando o blueprint de usuários e clubes
    from routes.routes import usuarios_bp, clubes_bp, auth_bp
    # registros de blueprints
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(clubes_bp)
    app.register_blueprint(auth_bp)

    return app
