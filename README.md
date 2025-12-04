# Gestão Barber
Projeto de gerenciamento de agendamento de horários para barbearia.

## Visão rápida

Este repositório contém uma aplicação Django para gerenciar uma barbearia.

## Pré-requisitos

- Python 3.10+ (recomendado)
- Git
- (Opcional) virtualenv/venv

## Configuração inicial (setup)

1. Clone o repositório (se ainda não tiver):

```bash
git clone <URL_DO_REPOSITORIO>
cd gestao_barber
```

2. Criar e ativar um ambiente virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Atualizar pip e instalar dependências:

Se houver `requirements.txt` no repositório:

```bash
pip install -U pip
pip install -r requirements.txt
```

Se não houver `requirements.txt`, instale Django (ou as dependências necessárias):

```bash
pip install -U pip
pip install django
```

4. (Opcional) configurar variáveis de ambiente

Se o projeto usar variáveis de ambiente (SECRET_KEY, DEBUG, etc.), crie um arquivo `.env` ou exporte as variáveis antes de rodar o servidor. Este repositório usa SQLite por padrão (`db.sqlite3`).

## Comandos úteis do Django

- Aplicar migrations:

```bash
python manage.py migrate
```

- Criar um superuser (administrador):

```bash
python manage.py createsuperuser
```

- Rodar o servidor de desenvolvimento:

```bash
python manage.py runserver 0.0.0.0:8000
```

- Rodar os testes:

```bash
python manage.py test
```

- Verificar checagens do projeto:

```bash
python manage.py check
```

- Ver migrations pendentes para uma app (ex: `estacaobarber`):

```bash
python manage.py makemigrations --dry-run --verbosity 3
```

## Banco de dados

Este projeto usa SQLite por padrão (arquivo `db.sqlite3`). Para backups simples, copie o arquivo:

```bash
cp db.sqlite3 db.sqlite3.backup
```

Se quiser trocar para outro banco (Postgres, MySQL), atualize `settings.py` e instale o adaptador correspondente.

## Git — fluxos e comandos para trabalhar com branches

Comandos básicos para sincronizar e trabalhar com branches remotas e locais.

- Atualizar referências remotas e limpar branches deletados no servidor:

```bash
git fetch --all --prune
```

- Listar branches locais e remotas:

```bash
git branch         # locais
git branch -r      # remotas
git branch -a      # todos
```

- Criar e trocar para uma branch local a partir de uma remota (ex.: `tela_cliente`):

```bash
git fetch origin
git checkout -b tela_cliente origin/tela_cliente
```

- Alternar para uma branch local existente e puxar alterações:

```bash
git checkout minha-branch
git pull origin minha-branch
```

- Atualizar a branch atual com mudanças da `main` (do servidor):

Rebase (linha mais limpa, reescreve histórico local):

```bash
git fetch origin
git rebase origin/main
```

Merge (mais seguro, preserva histórico):

```bash
git fetch origin
git merge origin/main
```

- Criar uma nova branch e enviar para o remoto:

```bash
git checkout -b minha-feature
git push -u origin minha-feature
```

- Puxar (pull) de uma branch remota para atualizar a local e resolver conflitos:

```bash
git checkout branch-alvo
git pull --rebase origin branch-alvo
# Se houver conflitos: editar arquivos, depois
git add <arquivos-resolvidos>
git rebase --continue   # ou git commit (se estiver usando merge)
```

- Forçar push (use com cuidado):

```bash
git push --force-with-lease origin minha-branch
```

Observações sobre pull/rebase vs pull/merge:

- `git pull --rebase` reaplica seus commits no topo das alterações remotas — resulta em histórico linear.
- `git pull` (merge) cria um commit de merge quando houver divergências.

## Dicas para resolver conflitos

1. Ao encontrar conflitos, abra os arquivos indicados por `git status`.
2. Localize os marcadores `<<<<`, `====`, `>>>>` e escolha a versão correta.
3. Após ajustar, rode:

```bash
git add <arquivos>
git rebase --continue    # se estiver em rebase
# ou
git commit                # se estiver em merge
```

4. Termine com `git push` para enviar as alterações ao remoto.

## Fluxo rápido (exemplo comum)

```bash
# atualizar referências
git fetch --all --prune

# criar branch a partir da main atualizada
git checkout main
git pull origin main
git checkout -b minha-feature

# trabalhar, commitar
git add .
git commit -m "Minha feature"

# enviar para o remoto
git push -u origin minha-feature
```

## Se algo der errado

- Verifique se o ambiente virtual está ativado
- Confirme a versão do Python: `python --version`
- Confirme se instalou as dependências corretas
- Para problemas com migrations, tente `python manage.py migrate --traceback` e revise o erro


---

Arquivo atualizado automaticamente com comandos básicos para iniciar o projeto e instruções Git.
