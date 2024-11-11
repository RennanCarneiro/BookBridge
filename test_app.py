# test_app.py
import unittest
from app.app import create_app
from app.database import db
from app.models import Usuario, Clube, Livro, Avaliacao


class BookBridgeTestCase(unittest.TestCase):
    def setUp(self):
        """Configurações iniciais antes de cada teste."""
        self.app = create_app()
        self.app_context = self.app.app_context()  # Cria o contexto da aplicação
        self.app_context.push()  # Ativa o contexto da aplicação
        self.client = self.app.test_client()

        # Configuração do banco de dados para testes
        db.create_all()

        # Criar um usuário para autenticação nos testes
        self.client.post('/usuarios', json={
            "nome": "Usuario Teste",
            "email": "teste@example.com",
            "senha": "senha_teste"
        })

        # Login para obter o token JWT
        response = self.client.post('/login', json={
            "email": "teste@example.com",
            "senha": "senha_teste"
        })
        response_data = response.get_json()

        # Verificar se o token foi retornado com sucesso
        self.token = response_data.get('token') if response.status_code == 200 else None
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def tearDown(self):
        """Limpeza após cada teste."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()  # Remove o contexto da aplicação

    def test_create_usuario(self):
        """Testa a criação de um novo usuário."""
        data = {
            "nome": "Usuario Teste 2",
            "email": "teste2@example.com",
            "senha": "senha_teste2"
        }
        response = self.client.post('/usuarios', json=data)
        response_data = response.get_json()
        print(f"Response Data: {response_data}")
        self.assertEqual(response.status_code, 201)
        self.assertIn("Usuário criado com sucesso!", response_data["message"])

    def test_get_usuarios(self):
        """Testa a listagem de usuários"""
        self.test_create_usuario()  # Cria um usuário para teste
        response = self.client.get('/usuarios')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data), 1)

    def test_update_usuario(self):
        """Testa a atualização de um usuário"""
        self.test_create_usuario()
        usuario = Usuario.query.first()
        response = self.client.put(f'/usuarios/{usuario.id}', json={
            'nome': 'João Atualizado',
            'email': 'joao.atualizado@example.com'
        })
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuário atualizado com sucesso!', data['message'])

    def test_delete_usuario(self):
        """Testa a exclusão de um usuário"""
        self.test_create_usuario()
        usuario = Usuario.query.first()
        response = self.client.delete(f'/usuarios/{usuario.id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuário deletado com sucesso!', data['message'])

    def test_create_clube(self):
        """Testa a criação de um clube"""
        # Verifique se o token está disponível antes de prosseguir com o teste
        self.assertIsNotNone(self.token, "Token de autenticação não foi gerado.")

        response = self.client.post('/clubes', json={
            "nome": "Clube Teste",
            "descricao": "Descrição do Clube Teste"
        }, headers=self.headers)

        response_data = response.get_json()
        print(f"Response Data: {response_data}")
        self.assertEqual(response.status_code, 201)
        self.assertIn("Clube criado com sucesso!", response_data["message"])

    def test_list_clubes(self):
        """Testa a listagem de clubes"""
        self.test_create_clube()  # Cria um clube para teste
        response = self.client.get('/clubes')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(data), 1)

    def test_add_livro(self):
        """Testa a adição de um livro a um clube"""
        self.test_create_clube()  # Cria um clube para adicionar o livro

        response = self.client.post('/clubes/1/livros', json={
            "titulo": "Livro Teste",
            "autor": "Autor Teste"
        }, headers=self.headers)

        response_data = response.get_json()
        print(f"Response Data: {response_data}")
        self.assertEqual(response.status_code, 201)
        self.assertIn("Livro adicionado com sucesso!", response_data["message"])

    def test_get_estatisticas(self):
        """Testa o endpoint de estatísticas"""
        response = self.client.get('/estatisticas')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('media_avaliacoes', data)
        self.assertIn('media_livros_por_clube', data)


if __name__ == '__main__':
    unittest.main()
