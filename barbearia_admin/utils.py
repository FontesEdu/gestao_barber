import requests
import re
from django.conf import settings

def limpar_e_formatar_numero(telefone_sujo):
    # Remove tudo que não é número
    apenas_numeros = re.sub(r'\D', '', str(telefone_sujo))
    # Garante o código do Brasil (55)
    if not apenas_numeros.startswith('55'):
        apenas_numeros = '55' + apenas_numeros
    return apenas_numeros

def enviar_notificacao_whatsapp(nome, telefone, data, horario):
    numero_limpo = limpar_e_formatar_numero(telefone)
    
    # Monta a URL usando as variáveis EXATAS do seu settings.py
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
    
    payload = {
        "number": numero_limpo,
        "text": (
            f"Olá, *{nome}*! ✂️\n\n"
            f"Seu agendamento na *Estação Barber* foi confirmado!\n"
            f"📅 Data: {data}\n"
            f"⏰ Horário: {horario}\n\n"
            f"Te esperamos lá!"
        )
    }
    
    headers = {
        "Content-Type": "application/json",
        "apikey": settings.EVOLUTION_API_KEY # Essa é a chave que você pegou na Evolution
    }

    try:
        # Timeout de 10 segundos para não travar o Django caso a API demore
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # O Render/Evolution costuma retornar 201 (Created)
        if response.status_code in [200, 201]:
            print(f"✅ WhatsApp enviado com sucesso para {nome}")
            return True
        else:
            print(f"❌ Erro na API Evolution: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ Erro crítico ao conectar com a API: {e}")
        return False