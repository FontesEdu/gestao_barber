from django.db import models
from django.utils import timezone

class HorarioDisponivel(models.Model):
    data = models.DateField(default=timezone.now)
    horario = models.TimeField()

    def __str__(self):
        return f"{self.data} - {self.horario.strftime('%H:%M')} ({self.barbeiro})"
        
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.nome