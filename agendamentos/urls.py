from django.urls import path
from agendamentos import views

urlpatterns = [
    path('', views.tela_agendamento, name='tela_agendamento'),
    path('disponibilidade/', views.ver_disponibilidade, name='ver_disponibilidade'),
    path("confirmar/", views.confirmar_agendamento, name="confirmar_agendamento"),
    path('finalizar/', views.finalizar_agendamento, name='finalizar_agendamento')
]