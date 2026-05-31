import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega a sua chave do .env
load_dotenv()

# Configura o Google
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("\n🔍 Buscando modelos liberados para a sua chave...\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Modelo Liberado: {m.name}")
except Exception as e:
    print(f"❌ Erro ao consultar o Google: {e}")
    
print("\n")