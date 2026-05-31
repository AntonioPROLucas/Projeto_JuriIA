from agno.tools.googlecalendar import GoogleCalendarTools
import os

# Certifique-se de que o arquivo está na mesma pasta que este script
CREDENTIALS_PATH = "credentials.json" 

print("Iniciando a autenticação...")

# Instanciando a ferramenta
calendar_tools = GoogleCalendarTools(
    credentials_path=CREDENTIALS_PATH,
    # O 'token_file' força o sistema a salvar o token onde queremos
    token_file="token.json",
    allow_update=True
)

# Tentando listar eventos
try:
    events = calendar_tools.list_events()
    print("Sucesso! Você tem acesso à agenda.")
except Exception as e:
    print(f"Erro ao conectar: {e}")