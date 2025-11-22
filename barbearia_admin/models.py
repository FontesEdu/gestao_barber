from django.db import models
from django.utils import timezone

# Create your models here.
class Disponibilidade(models.Model):
    data = models.DateField(default=timezone.now)
    horario = models.TimeField()
    
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.data} - {self.horario.strftime('%H:%M')})"

class Agendamento(models.Model):
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=20)
    data = models.DateField(default=timezone.now)
    horario = models.TimeField(default=timezone.now)

    class Meta:
        unique_together = ('data', 'horario')

    def __str__(self):
        return f"{self.nome} - {self.data} {self.horario}"
    