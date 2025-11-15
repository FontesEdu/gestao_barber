from django.urls import path
from estacaobarber import views

urlpatterns = [
    path('', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('sucesso/', views.cadastro_sucesso, name='cadastro_sucesso')
    
]