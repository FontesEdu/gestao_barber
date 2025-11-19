from django.shortcuts import render, redirect
from django.urls import reverse

def cadastro_sucesso(request):
    return render(request, 'sucesso.html')

def tela_inicial(request):
    return render(request, 'home.html')