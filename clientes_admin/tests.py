from django.test import TestCase, Client
from django.urls import reverse
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from clientes_admin.models import Categoria, Servico

class ClientesFullTest(TestCase):
    def setUp(self):
        # Preparo o ambiente: crio uma categoria e um serviço de exemplo
        self.client = Client()
        self.cat = Categoria.objects.create(nome="Cabelo")
        self.servico = Servico.objects.create(
            nome="Corte Tesoura",
            descricao="Detalhado",
            preco=50.00,
            tempo_estimado=timedelta(minutes=45)
        )
        # Vinculo o serviço à categoria para testar os filtros depois
        self.servico.categorias.add(self.cat)

    def test_tela_inicial_completa(self):
        # Testando a "vitrine" do app:
        # Primeiro, vejo se a home abre mesmo sem nenhuma imagem cadastrada
        response = self.client.get(reverse("tela_inicial"))
        self.assertEqual(response.status_code, 200)
        
        # Agora forço uma situação com foto para garantir que o front-end não quebre o layout
        foto = SimpleUploadedFile(name='test.jpg', content=b'', content_type='image/jpeg')
        Categoria.objects.create(nome="Barba", foto=foto)
        response = self.client.get(reverse("tela_inicial"))
        
        self.assertEqual(response.status_code, 200)
        # Verifico se a lista de categorias está realmente chegando no contexto da página
        self.assertIn('categorias', response.context)

    def test_servicos_por_categoria(self):
        # Validando o filtro: se eu clicar em "Cabelo", tem que aparecer o "Corte Tesoura"
        response = self.client.get(reverse("servicos_por_categoria", args=[self.cat.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Corte Tesoura")
        
        # Testo o comportamento do sistema caso tentem acessar uma categoria que não existe (ID 999)
        response = self.client.get(reverse("servicos_por_categoria", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_detalhes_servico(self):
        # Entrando na página do serviço:
        # Importante: verifico se o preço aparece formatado (ex: 50,00) como manda o padrão PT-BR
        response = self.client.get(reverse("detalhes_servico", args=[self.servico.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "50,00") 
        
        # Garanto que um ID de serviço inválido jogue para a página de erro 404
        response = self.client.get(reverse("detalhes_servico", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_cadastro_sucesso(self):
        # Só confirmando se a página final de "Agendamento Realizado" está carregando ok
        response = self.client.get(reverse("cadastro_sucesso"))
        self.assertEqual(response.status_code, 200)

    def test_model_str(self):
        # Esse aqui é pro "ajuste fino" do Coverage:
        # Testo se o método __str__ dos models retorna o texto certo (ajuda muito no Admin do Django)
        self.assertEqual(str(self.cat), "Cabelo")
        self.assertIn("Corte Tesoura", str(self.servico))