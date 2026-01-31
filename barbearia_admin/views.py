from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date, timedelta
from .models import Disponibilidade, Agendamento
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django_ratelimit.decorators import ratelimit
import json
from django.db.utils import IntegrityError 
from .utils import enviar_notificacao_whatsapp


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
        "horarios_hoje": json.dumps([str(h) for h in horarios_hoje])  
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
    data = request.GET.get("data")
    horario = request.GET.get("horario")
    if not data or not horario:
        return HttpResponse("Erro: data ou horário inválidos.", status=400)
    return render(request, "confirmar_agendamento.html", {"data": data, "horario": horario})



# Finaliza o agendamento, com limite de 3 tentativas por dia

@ratelimit(key='ip', rate='3/d', block=True)
def finalizar_agendamento(request):
    if request.method != "POST":
        return HttpResponse("Método inválido.", status=405)

    # 1. Coleta de dados do POST
    nome = request.POST.get("nome")
    telefone = request.POST.get("telefone")
    data_str = request.POST.get("data")
    horario = request.POST.get("horario")

    # Validação básica de presença de dados
    if not all([nome, telefone, data_str, horario]):
        return HttpResponse("Todos os campos são obrigatórios.", status=400)

    # 2. Tratamento da Data
    try:
        data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return HttpResponse("Formato de data inválido.", status=400)

    # 3. Verificação de Disponibilidade
    try:
        # Buscamos a disponibilidade específica
        disp = Disponibilidade.objects.get(data=data_obj, horario=horario)
        
        # Se por algum motivo ela já estiver marcada como indisponível no banco
        if not disp.disponivel:
             return HttpResponse("Este horário acabou de ser ocupado por outro cliente.", status=409)
             
    except Disponibilidade.DoesNotExist:
        return HttpResponse("Erro: Horário não encontrado no sistema.", status=400)

    # 4. Criação do Agendamento e Atualização da Disponibilidade
    try:
        # Criamos o registro do agendamento
        Agendamento.objects.create(
            nome=nome,
            telefone=telefone,
            data=data_obj,
            horario=horario
        )
        
        # Marcamos como ocupado para não aparecer mais para outros
        disp.disponivel = False
        disp.save()

    except IntegrityError:
        # Caso dois usuários cliquem exatamente ao mesmo tempo no último segundo
        return HttpResponse("Erro: Este horário já foi agendado por outra pessoa.", status=409)

    # 5. DISPARO DA NOTIFICAÇÃO (WhatsApp)
    # Formatamos a data para o padrão brasileiro DD/MM/AAAA para a mensagem ficar bonita
    data_formatada_br = data_obj.strftime("%d/%m/%Y")
    
    # Chamamos a função do seu utils.py
    enviar_notificacao_whatsapp(nome, telefone, data_formatada_br, horario)

    # 6. Renderização de Sucesso
    return render(request, "sucesso.html", {
        "nome": nome,
        "data": data_formatada_br,
        "horario": horario,
        "telefone": telefone
    })

# Painel administrativo que mostra horários, agendados e livres

def painel_adm(request, data=None):
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

    agora = datetime.now()

    # Busca agendamentos do dia
    agendamentos = Agendamento.objects.filter(data=hoje)
    agendados_dict = {ag.horario: ag for ag in agendamentos}

    for h in horarios:
        h.passou = datetime.combine(h.data, h.horario) < agora
        # Adiciona cliente (ou None se não houver)
        h.cliente = agendados_dict.get(h.horario)

    total_horarios = horarios.count()
    total_agendados = len(agendamentos)
    total_livres = total_horarios - total_agendados

    return render(request, "admin/painel_adm.html", {
        "hoje": hoje,
        "horarios": horarios,
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
    data_str = request.GET.get("data")
    if not data_str:
        return render(request, "ver_calendario.html")

    # Converte para date
    data_obj = date.fromisoformat(data_str)

    # Todos os horários cadastrados para a data
    disponibilidades = Disponibilidade.objects.filter(data=data_obj).order_by("horario")

    # Horários já agendados
    agendados = Agendamento.objects.filter(data=data_obj).values_list("horario", flat=True)

    agora = datetime.now()
    horarios_livres = []

    for h in disponibilidades:
        # Remove horários já agendados
        if h.horario in agendados:
            continue

        # Se for hoje, remove horários que já passaram
        if data_obj == agora.date() and datetime.combine(h.data, h.horario) <= agora:
            continue

        # Formata em HH:MM
        horarios_livres.append(h.horario.strftime("%H:%M"))

    return render(request, "ver_disponibilidade.html", {
        "data_selecionada": data_obj,
        "horarios_livres": horarios_livres
    })


def ver_horarios(request):
    data_str = request.GET.get('data')
    hoje = date.fromisoformat(data_str) if data_str else date.today()

    horarios = Disponibilidade.objects.filter(data=hoje).order_by("horario")
    agendamentos_qs = Agendamento.objects.filter(data=hoje)
    agendados_dict = {ag.horario: ag.nome for ag in agendamentos_qs}

    for h in horarios:
        if datetime.combine(h.data, h.horario) < datetime.now():
            h.status = "passado"
            h.nome_cliente = ""
        elif h.horario in agendados_dict:
            h.status = "agendado"
            h.nome_cliente = agendados_dict[h.horario]
        else:
            h.status = "livre"
            h.nome_cliente = ""

    context = {
        'hoje': hoje,
        'horarios': horarios,
        'total_horarios': horarios.count(),
        'total_agendados': len(agendados_dict),
        'total_livres': horarios.count() - len(agendados_dict),
    }

    return render(request, 'ver_horarios.html', context)