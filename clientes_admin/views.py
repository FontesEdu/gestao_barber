from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
    
def tela_inicial(request):
    categorias = Categoria.objects.all()
    fotos = [categoria.foto.url for categoria in categorias if categoria.foto]
    return render(request, "home.html", {"categorias": categorias}, {"fotos": fotos})

def servicos_por_categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    servicos = Servico.objects.filter(categorias=categoria)
    return render(request, "servicos_por_categoria.html", {
        "categoria": categoria,
        "servicos": servicos
    })

def detalhes_servico(request, id):
    servico = Servico.objects.get(id=id)
    return render(request, "detalhes_servico.html", {"servico": servico}) 

def cadastro_sucesso(request):
    return render()