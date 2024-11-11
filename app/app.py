# app/app.py

from flask import Flask  # Importando a biblioteca Flask
from flask_sqlalchemy import SQLAlchemy  # Importando o SQLAlchemy para o banco de dados
from flask_migrate import Migrate

# Inicializando o banco de dados e o sistema de migração
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)  # Instanciando a aplicação Flask

    # Configurações da aplicação e do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:senha@localhost/bookbridge'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializando o banco de dados e o sistema de migração com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)

    # Importando e registrando o blueprint de usuários e clubes
    from routes.routes import usuarios_bp
    from routes.routes import usuarios_bp, clubes_bp
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(clubes_bp)

    return app
