from django.db import models
from django.utils import timezone
        
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.nome