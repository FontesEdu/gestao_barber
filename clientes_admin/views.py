from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Servico

def tela_inicial(request):
    categorias = Categoria.objects.all()
    # Lista com URLs de fotos (caso existam)
    fotos = [categoria.foto.url for categoria in categorias if categoria.foto]

    contexto = {
        "categorias": categorias,
        "fotos": fotos,
    }

    return render(request, "home.html", contexto)


def servicos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    servicos = Servico.objects.filter(categorias=categoria)

    contexto = {
        "categoria": categoria,
        "servicos": servicos,
    }

    return render(request, "servicos_por_categoria.html", contexto)


def detalhes_servico(request, id):
    servico = get_object_or_404(Servico, id=id)

    contexto = {
        "servico": servico
    }

    return render(request, "detalhes_servico.html", contexto)


def cadastro_sucesso(request):
    return render(request, "cadastro_sucesso.html")
