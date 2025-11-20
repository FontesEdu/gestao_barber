from django.urls import path
from estacaobarber import views

urlpatterns = [
    path('', views.tela_inicial, name='tela_inicial'),
    path('sucesso/', views.cadastro_sucesso, name='cadastro_sucesso')
    
]