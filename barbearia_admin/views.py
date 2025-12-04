from django.shortcuts import render, redirect
from .models import *
from datetime import datetime, date, time, timedelta
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django_ratelimit.decorators import ratelimit
import json


def tela_agendamento(request):
    from django.utils import timezone

    hoje = timezone.localdate()

    horarios_hoje = list(
        Disponibilidade.objects.filter(data=hoje)
        .values_list("horario", flat=True)
    )

    datas_disponiveis = (
        Disponibilidade.objects
        .values('data')
        .annotate(total=Count('id'))
        .filter(total__gt=0)
        .values_list('data', flat=True)
    )

    import json
    datas_formatadas = json.dumps([d.strftime("%Y-%m-%d") for d in datas_disponiveis])

    return render(request, "ver_calendario.html", {
        "datas_disponiveis": datas_formatadas,
        "horarios_hoje": json.dumps([str(h) for h in horarios_hoje])  # 🔥 AQUI
    })


def ver_disponibilidade(request):
    data_selecionada = request.GET.get('data')

    if not data_selecionada:
        return render(request, 'ver_calendario.html')

    disponibilidades = Disponibilidade.objects.filter(data=data_selecionada)

    horarios_totais = [d.horario for d in disponibilidades]

    agendados = Agendamento.objects.filter(
        data=data_selecionada
    ).values_list("horario", flat=True)

    horarios_livres = [
        h.strftime("%H:%M") for h in horarios_totais if h not in agendados
    ]

    return render(
        request,
        'ver_disponibilidade.html',
        {
            'data_selecionada': data_selecionada,
            'horarios_livres': horarios_livres
        }
    )


def confirmar_agendamento(request):
    data = request.GET.get("data")
    horario = request.GET.get("horario")

    if not data or not horario:
        return HttpResponse("Erro: data ou horário inválidos.")

    return render(request, "confirmar_agendamento.html", {
        "data": data,
        "horario": horario
    })

@ratelimit(key='ip', rate='3/d', block=True)
def finalizar_agendamento(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        data = request.POST.get("data")
        horario = request.POST.get("horario")

        Agendamento.objects.create(
            nome=nome,
            telefone=telefone,
            data=data,
            horario=horario
        )
        try:
            disp = Disponibilidade.objects.get(data=data, horario=horario)
            disp.disponivel = False
            disp.save()
        except Disponibilidade.DoesNotExist:
            pass

        return render(request, "sucesso.html", {
            "nome": nome,
            "data": data,
            "horario": horario
        })


    return HttpResponse("Método inválido.")
