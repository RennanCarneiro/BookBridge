# create_tables.py

from app.app import create_app, db

# Cria a aplicação e o contexto para criar as tabelas
app = create_app()

with app.app_context():
    db.drop_all()  # Remove as tabelas existentes (cuidado com perda de dados)
    db.create_all()  # Cria as tabelas novamente com as novas configurações
    print("Tabelas recriadas com sucesso!")
