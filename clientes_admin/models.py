from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    foto = models.ImageField(upload_to='categorias/', blank=True, null=True)

    def __str__(self):
        return self.nome

class Servico(models.Model):

    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='servicos/', blank=True, null=True)
    tempo_estimado = models.DurationField(default=timezone.timedelta(minutes=30))
    categorias = models.ManyToManyField(Categoria, related_name="servicos")


    def __str__(self):
        return f"{self.nome} - R${self.preco:.2f}"