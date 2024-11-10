from flask import Flask #importando biblioteca flask
from flask_sqlalchemy import SQLAlchemy #importando para o banco de dados
from flask_migrate import Migrate

app = Flask('__name__') #instanciando uma variavel
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:senha@localhost/bookbridge'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'app': app}  # Torna db e app acessíveis no Flask shell

if __name__ == '__main__':
    app.run(debug=True)  # Comando para rodar a aplicação