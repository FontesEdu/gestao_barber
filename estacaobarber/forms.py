from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(xx) xxxxx-xxxx'}),
        }