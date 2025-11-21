from django.db import models
from django.utils import timezone
        
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)
    
class Corte(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='cortes/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - R${self.preco}"