from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date, timedelta
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django_ratelimit.decorators import ratelimit
import json


# Tela inicial onde o cliente escolhe a data
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
    # Converte datas para string JSON
    datas_formatadas = json.dumps([d.strftime("%Y-%m-%d") for d in datas_disponiveis])

    return render(request, "ver_calendario.html", {
        "datas_disponiveis": datas_formatadas,
        "horarios_hoje": json.dumps([str(h) for h in horarios_hoje])  # 🔥 AQUI
    })


def ver_disponibilidade(request):
    # Pega a data escolhida pelo usuário
    data_selecionada = request.GET.get('data')

    if not data_selecionada:
        return render(request, 'ver_calendario.html')

    # Busca todos os horários cadastrados para o dia
    disponibilidades = Disponibilidade.objects.filter(data=data_selecionada)

    # Lista de horários existentes
    horarios_totais = [d.horario for d in disponibilidades]

    # Busca horários já agendados
    agendados = Agendamento.objects.filter(
        data=data_selecionada
    ).values_list("horario", flat=True)

    # Filtra os horários que ainda estão disponíveis
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


# Tela de confirmação do agendamento
def confirmar_agendamento(request):
    # Recupera os dados enviados
    data = request.GET.get("data")
    horario = request.GET.get("horario")

    if not data or not horario:
        return HttpResponse("Erro: data ou horário inválidos.")

    return render(request, "confirmar_agendamento.html", {
        "data": data,
        "horario": horario
    })


# Finaliza o agendamento, com limite de 3 tentativas por dia
@ratelimit(key='ip', rate='3/d', block=True)
def finalizar_agendamento(request):
    # Aceita apenas POST
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        data = request.POST.get("data")
        horario = request.POST.get("horario")

        # Cria o agendamento
        Agendamento.objects.create(
            nome=nome,
            telefone=telefone,
            data=data,
            horario=horario
        )

        # Marca disponibilidade como ocupada
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


# Painel administrativo que mostra horários, agendados e livres

def painel_adm(request, data=None):
    # Se recebeu data pela URL, usa ela
    if data:
        hoje = datetime.strptime(data, "%Y-%m-%d").date()
    else:
        hoje = request.GET.get("data")
        if hoje:
            hoje = datetime.strptime(hoje, "%Y-%m-%d").date()
        else:
            hoje = datetime.today().date()

    # Busca disponibilidades do dia
    horarios = Disponibilidade.objects.filter(data=hoje).order_by("horario")

    # >>> AQUI ENTRA A LÓGICA DE HORÁRIO PASSADO <<<
    agora = datetime.now()

    for h in horarios:
        if datetime.combine(h.data, h.horario) < agora:
            h.passou = True
        else:
            h.passou = False

    # Mapeia agendamentos pelo horário para exibição rápida
    agendados = {
        ag.horario: ag
        for ag in Agendamento.objects.filter(data=hoje)
    }

    # Contadores gerais
    total_horarios = horarios.count()
    total_agendados = len(agendados)
    total_livres = total_horarios - total_agendados

    return render(request, "admin/painel_adm.html", {
        "hoje": hoje,
        "horarios": horarios,
        "agendados": agendados,
        "total_horarios": total_horarios,
        "total_agendados": total_agendados,
        "total_livres": total_livres
    })


# Remove um horário específico
def remover_horario(request, id):
    # Busca e apaga um horário
    horario = get_object_or_404(Disponibilidade, id=id)
    dia = horario.data
    horario.delete()

    return redirect(f"/agendamentos/painel_adm/?dia={dia}")


# Gera automaticamente todos os horários de um dia

def gerar_disponibilidades(request):
    dia = request.GET.get("dia")

    inicio = datetime.strptime("08:00", "%H:%M")
    fim = datetime.strptime("20:00", "%H:%M")

    atual = inicio
    while atual <= fim:
        Disponibilidade.objects.get_or_create(
            data=dia,
            horario=atual.time()
        )
        atual += timedelta(minutes=30)

    return redirect(f"/agendamentos/painel_adm/?dia={dia}")

def remover_horario(request, id):
    Disponibilidade.objects.filter(id=id).delete()
    return redirect(request.META.get("HTTP_REFERER", "painel_adm"))

def ver_disponibilidade(request):
    data = request.GET.get("data")
    horarios = Horario.objects.filter(data=data)

    agora = datetime.now()

    for h in horarios:
        # Se a data/hora do horário já passou marca como indisponível
        if datetime.combine(h.data, h.horario) < agora:
            h.indisponivel = True

    return render(request, "disponibilidade.html", {"horarios": horarios})

from datetime import datetime, date
from .models import Disponibilidade, Agendamento

def ver_horarios(request):
    # pegar a data enviada por GET ou usar hoje
    data_str = request.GET.get('data')
    if data_str:
        hoje = date.fromisoformat(data_str)
    else:
        hoje = date.today()

    # buscar todos os horários do dia
    horarios = Disponibilidade.objects.filter(data=hoje).order_by("horario")

    # buscar agendamentos do dia
    agendados_qs = Agendamento.objects.filter(data=hoje).values_list('horario', flat=True)

    # marcar status de cada horário
    for h in horarios:
        if datetime.combine(h.data, h.horario) < datetime.now():
            h.status = "passado"
        elif h.horario in agendados_qs:
            h.status = "agendado"
        else:
            h.status = "livre"

    total_horarios = horarios.count()
    total_agendados = len(agendados_qs)
    total_livres = total_horarios - total_agendados

    context = {
        'hoje': hoje,
        'horarios': horarios,
        'total_horarios': total_horarios,
        'total_agendados': total_agendados,
        'total_livres': total_livres,
    }

    return render(request, 'ver_horarios.html', context)


