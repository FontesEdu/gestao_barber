from django.urls import path
from clientes_admin import views

urlpatterns = [
    path('', views.tela_inicial, name='tela_inicial'),
    path('sucesso/', views.cadastro_sucesso, name='cadastro_sucesso'),
    path('servico/<int:id>/', views.detalhes_servico, name='detalhes_servico'),
    path('categoria/<int:categoria_id>/', views.servicos_por_categoria, name='servicos_por_categoria'),
]