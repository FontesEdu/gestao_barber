from django.shortcuts import render, redirect
from django.urls import reverse

def cadastro_sucesso(request):
    return render(request, 'sucesso.html')

<<<<<<< HEAD
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastro_sucesso')  
    else:
        form = ClienteForm()
    return render(request, 'inicial.html', {'form': form})
=======
def tela_inicial(request):
    return render(request, 'home.html')
>>>>>>> formulario_agendamento
