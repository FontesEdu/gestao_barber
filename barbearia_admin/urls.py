from django.urls import path
from barbearia_admin import views

urlpatterns = [
    path('', views.tela_agendamento, name='tela_agendamento'),
    path('disponibilidade/', views.ver_disponibilidade, name='ver_disponibilidade'),
    path("confirmar/", views.confirmar_agendamento, name="confirmar_agendamento"),
    path('finalizar/', views.finalizar_agendamento, name='finalizar_agendamento'),
    path('painel_adm/', views.painel_adm, name='painel_adm'),
    path('painel_adm/<str:data>/', views.painel_adm, name='painel_adm_data'),    # Painel ADM: com data na URL → painel_adm/2025-12-04/
    path('remover_horario/<int:id>/', views.remover_horario, name='remover_horario'),# Remove um horário específico da disponibilidade
    path('ver_horarios/', views.ver_horarios, name='ver_horarios'),
]
