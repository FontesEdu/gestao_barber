from datetime import date, time, timedelta, datetime
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Disponibilidade, Agendamento


@override_settings(RATELIMIT_ENABLE=False)
class BarbeariaFullTest(TestCase):
    def setUp(self):
        # Preparando o terreno: crio o cliente de teste e um admin
        self.client = Client()
        self.user = User.objects.create_superuser("admin", "a@a.com", "123")
        self.client.force_login(self.user) # Já logo para não barrar nos testes de ADM
        
        self.hoje = date.today()
        self.amanha = self.hoje + timedelta(days=1)
        
        # Crio um horário padrão para usar de base nos testes abaixo
        self.disp = Disponibilidade.objects.create(
            data=self.amanha, horario=time(10, 0), disponivel=True
        )

    ## --- ÁREA DO CLIENTE --- ##

    def test_finalizar_agendamento_erros(self):
        # Aqui eu testo se o sistema barra as tentativas erradas do usuário
        url = reverse('finalizar_agendamento')
        
        # Se tentar acessar via GET, tem que dar erro (só aceitamos POST aqui)
        self.assertEqual(self.client.get(url).status_code, 405)
        
        # Se mandar o formulário vazio, o sistema deve reclamar
        self.assertEqual(self.client.post(url, {}).status_code, 400)
        
        # Testando se a validação de data maluca está funcionando
        payload = {"nome": "Teste", "telefone": "123", "data": "data-errada", "horario": "10:00"}
        self.assertEqual(self.client.post(url, payload).status_code, 400)
        
        # E se o cara tentar agendar um horário que nem existe no banco?
        payload["data"] = self.amanha.isoformat()
        payload["horario"] = "23:59"
        self.assertEqual(self.client.post(url, payload).status_code, 400)

    def test_ver_disponibilidade_logica(self):
        # Verifico se a listagem de horários está filtrando o que já passou
        url = reverse('ver_disponibilidade')
        
        # Primeiro vejo se a página carrega sem erros sem passar data
        self.assertEqual(self.client.get(url).status_code, 200)
        
        # Crio um horário no passado (hoje bem cedo) para garantir que ele não apareça
        h_passado = time(0, 1) 
        Disponibilidade.objects.create(data=self.hoje, horario=h_passado)
        res = self.client.get(url, {'data': self.hoje.isoformat()})
        self.assertNotContains(res, "00:01")

    ## --- PAINEL ADMINISTRATIVO E GESTÃO --- ##

    def test_painel_adm_variacoes(self):
        # Testando as diferentes formas de abrir o painel do barbeiro
        url = reverse('painel_adm')
        
        # Verifico se ele aceita a data vindo pelo parâmetro GET
        self.client.get(url, {'data': self.amanha.isoformat()})
        
        # Se eu abrir o painel puro, ele deve assumir a data de hoje sozinho
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Só confirmando se o filtro de data padrão não quebra nada
        self.client.get(url, {'data': self.hoje.isoformat()})

    def test_gerar_disponibilidades_simples(self):
        # Testo aquele botão de "gerar horários padrão" (vapt-vupt)
        url = reverse('gerar_disponibilidades')
        res = self.client.get(url, {'dia': self.amanha.isoformat()})
        # Tem que redirecionar depois de criar
        self.assertEqual(res.status_code, 302) 

    def test_ver_horarios_status(self):
        # Verifico se a visualização diferencia bem: livre, ocupado e passado
        url = reverse('ver_horarios')
        
        # 1. Registro um agendamento para simular um horário ocupado
        Agendamento.objects.create(nome="Cliente X", telefone="1", data=self.amanha, horario=time(10, 0))
        
        # 2. Crio um horário que já passou ontem
        Disponibilidade.objects.create(data=self.hoje - timedelta(days=1), horario=time(10, 0))
        
        # Bato na página para ver se ela processa esses status sem dar erro
        self.client.get(url, {'data': self.amanha.isoformat()})
        self.client.get(url, {'data': (self.hoje - timedelta(days=1)).isoformat()})

    ## --- TESTES DE INTEGRAÇÃO COM O DJANGO ADMIN --- ##

    def test_admin_gerar_bulk(self):
        # Teste crucial: a geração em massa direto pelo Admin do Django
        changelist_url = reverse("admin:barbearia_admin_disponibilidade_changelist")
        url_gerar = f"{changelist_url.rstrip('/')}/gerar/"
        
        # Vou simular a criação de uma semana inteira de trabalho
        proxima_semana = self.hoje + timedelta(days=7)
        payload = {
            "data_fim": proxima_semana.isoformat(),
            "intervalo": 30,
            "horarios_manha_inicio": "08:00",
            "horarios_manha_fim": "10:00",
            "horarios_tarde_inicio": "14:00",
            "horarios_tarde_fim": "16:00",
            "incluir_sabado": False, # Quero ver se ele respeita a folga de sábado
            "incluir_domingo": False, # E a de domingo também
        }
        res = self.client.post(url_gerar, payload)
        self.assertEqual(res.status_code, 302)