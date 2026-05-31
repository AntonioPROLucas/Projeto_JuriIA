from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .models import Cliente, Documentos
from ia.agents import JuriAi
import pypdf
from agno.knowledge.document import Document

def home(request):
    if request.method == 'POST':
        # Se o utilizador digitou um ID no "Modo Demonstração"
        cliente_id = request.POST.get('cliente_id')
        if cliente_id:
            # Redireciona automaticamente para a página do cliente correspondente
            return redirect('cliente', id=cliente_id)
            
    # Se for um acesso normal (GET), apenas renderiza a tela inicial
    return render(request, 'home.html')

# --- FUNÇÃO AUXILIAR PARA LER O PDF ---
def extrair_texto_pdf(caminho_pdf):
    texto = ""
    try:
        with open(caminho_pdf, "rb") as f:
            leitor = pypdf.PdfReader(f)
            for pagina in leitor.pages:
                texto += pagina.extract_text() or ""
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
    return texto

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senha e confirmar senha não são iguais.')
            return redirect('cadastro')
        
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'Sua senha deve ter pelo meno 6 caracteres.')
            return redirect('cadastro')
        
        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse username.')
            return redirect('cadastro')
        
        User.objects.create_user(username=username, password=senha)
        return redirect('login')

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        user = authenticate(username=username, password=senha)
        
        if user is not None:
            auth.login(request, user)
            return redirect('clientes')
        else:
            messages.add_message(request, constants.ERROR, 'Usuário ou senha inválidos.')
            return redirect('login')
        
@login_required
def clientes(request):
    if request.method == 'GET':
        clientes = Cliente.objects.filter(user=request.user)
        return render(request, 'clientes.html', {'clientes': clientes})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        tipo = request.POST.get('tipo')
        status = request.POST.get('status') == 'on'

        Cliente.objects.create(
            nome=nome, email=email, tipo=tipo, status=status, user=request.user
        )
        messages.add_message(request, constants.SUCCESS, 'Cliente cadastrado com sucesso!')
        return redirect('clientes')
    
@login_required
def cliente(request, id):
    cliente = Cliente.objects.get(id=id)
    
    if request.method == 'GET':
        documentos = Documentos.objects.filter(cliente=cliente)
        return render(request, 'cliente.html', {'cliente': cliente, 'documentos': documentos})
        
    elif request.method == 'POST':
        tipo = request.POST.get('tipo')
        documento = request.FILES.get('documento')
        data = request.POST.get('data')
        
        # Salva o arquivo fisicamente
        novo_documento = Documentos(
            cliente=cliente,
            tipo=tipo,
            arquivo=documento,
            data_upload=data
        )
        novo_documento.save()

        # Extração de texto para RAG e LangChain
        try:
            caminho_real = novo_documento.arquivo.path
            texto_pdf = extrair_texto_pdf(caminho_real)
            
            # Salva o texto na coluna 'content' para o LangChain ler depois
            novo_documento.content = texto_pdf
            novo_documento.save()
            
            if texto_pdf.strip():
                # Formata para o padrão Agno (Para a PsiQuete poder conversar sobre ele no chat)
                doc_agno = Document(
                    id=str(novo_documento.id),
                    name=novo_documento.arquivo.name,
                    content=texto_pdf,
                )
                JuriAi.knowledge.load_documents([doc_agno])
                messages.add_message(request, constants.SUCCESS, 'Documento salvo e indexado na IA!')
            else:
                messages.add_message(request, constants.WARNING, 'Salvo, mas o PDF parece estar vazio ou é uma imagem escaneada.')
                
        except Exception as e:
            print(f"Erro na indexação da IA: {e}")
            messages.add_message(request, constants.ERROR, 'Documento salvo, mas houve falha ao enviar para a IA.')

        return redirect(reverse('cliente', kwargs={'id': cliente.id}))