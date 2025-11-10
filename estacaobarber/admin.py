from django.contrib import admin
from .models import HorarioDisponivel

@admin.register(HorarioDisponivel)
class HorarioDisponivelAdmin(admin.ModelAdmin):
    list_display = ['horario']
