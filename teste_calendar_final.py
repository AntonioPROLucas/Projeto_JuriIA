from agno.tools.googlecalendar import GoogleCalendarTools
from django.conf import settings

# Simula a carga das ferramentas
tools = GoogleCalendarTools(
    credentials_path="credentials.json",
    calendar_id='primary'
)

# Tenta listar os próximos 5 eventos para ver se a API responde
try:
    eventos = tools.list_events()
    print("Sucesso! Conexão com o Google Calendar estabelecida.")
    print(eventos)
except Exception as e:
    print(f"Erro na conexão: {e}")