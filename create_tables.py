from app import app, db  # Importa a instância do Flask (app) e o db

# Cria todas as tabelas definidas nos modelos
with app.app_context():  # Estabelece o contexto de aplicação
    db.create_all()  # Cria as tabelas no banco de dados
    print("Tabelas criadas com sucesso!")
