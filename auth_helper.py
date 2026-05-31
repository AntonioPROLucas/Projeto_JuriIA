from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Define o escopo de acesso à agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

# O fluxo vai ler o seu credentials.json
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

# Isso força a abertura do navegador e salva o token num arquivo
creds = flow.run_local_server(port=0)

# Salva o token localmente
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("Sucesso! O ficheiro token.json foi criado com êxito.")