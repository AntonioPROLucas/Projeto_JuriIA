import json
import requests
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.tools import tool
from agno.vectordb.lancedb import LanceDb
from .literals import TribunalLiteral
from dotenv import load_dotenv
from tzlocal import get_localzone_name
from agno.tools.googlecalendar import GoogleCalendarTools
from agno.models.google import Gemini
from tzlocal import get_localzone_name
import datetime
from django.conf import settings

load_dotenv()

calendar_tools = GoogleCalendarTools(
    credentials_path=settings.BASE_DIR / "credentials.json",
    calendar_id='primary'
)

@tool
def search_datajud_api(tribunal: TribunalLiteral, process_number: str) -> str:
    """
    Busca informações de um processo judicial na API pública do DataJud (CNJ).
    
    Realiza uma consulta na API pública do Conselho Nacional de Justiça
    para obter dados de um processo judicial específico em um determinado tribunal.
    
    Args:
        tribunal: Código do tribunal onde o processo está tramitando.
            Valores aceitos: "tst", "tse", "stj", "stm", "trf1"-"trf6", 
            "tjsp", "tjmg", etc. (ver TribunalLiteral para lista completa).
        process_number: Número do processo judicial no formato CNJ
            (ex: "00008323520184013202").
    
    Returns:
        Resposta da API em formato JSON como string contendo os dados do processo,
        incluindo informações como número, partes, movimentações, decisões, etc.
        Retorna JSON com campo "error" em caso de falha na requisição.
    """

    url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"
    payload = {
        "query": {
            "match": {
                "numeroProcesso": process_number
            }
        }
    }
    headers = {
        "Authorization": f"APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return json.dumps({"error": str(e)})
    
class JuriAi:
    DATAJUD_BASE_URL = "https://api-publica.datajud.cnj.jus.br"
    DATAJUD_API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
    VECTOR_DB_TABLE = "documentos"
    VECTOR_DB_URI = "lancedb"
    MEMORY_DB_FILE = "db.sqlite3"
    MEMORY_TABLE = "my_memory_table"
    AGENT_NAME = "Assistente Jurídico Virtual"
    AGENT_DESCRIPTION = (
        "Assistente virtual especializado em questões jurídicas com acesso "
        "a base de conhecimento e consulta de processos judiciais."
    )

    INSTRUCTIONS = """
    SUAS CAPACIDADES:
    1. Acesso a Base de Conhecimento (RAG): Você possui acesso a um banco de dados vetorial contendo documentos enviados pelo usuário.
    2. Consulta de Processos: Você pode buscar informações sobre processos judiciais através da API do DataJud (CNJ).
    
    DIRETRIZES E REGRAS DE OURO:
    - SEMPRE que o usuário pedir um resumo, perguntar sobre "documentos", "petição", "contratos", ou mencionar "fatos", você DEVE OBRIGATORIAMENTE utilizar a sua ferramenta de busca na base de conhecimento (knowledge base) ANTES de responder.
    - NUNCA diga que não tem acesso a documentos ou que não pode lê-los. Assuma sempre que a resposta está na sua base de conhecimento e pesquise lá primeiro.
    - Ao consultar processos no CNJ, forneça informações claras e organizadas.
    - Se não tiver certeza sobre alguma informação após pesquisar na base, indique isso ao usuário, mas comprove que efetuou a pesquisa.
    - Mantenha um tom profissional e objetivo em todas as respostas.
    """

    knowledge = Knowledge(
        vector_db=LanceDb(
            table_name=VECTOR_DB_TABLE,
            uri=VECTOR_DB_URI,
            embedder=GeminiEmbedder(id="models/embedding-001") 
        ),
    )

    @classmethod
    def build_agent(cls, knowledge_filters: dict = {}) -> Agent:
        db = SqliteDb(
            db_file=cls.MEMORY_DB_FILE,
            memory_table=cls.MEMORY_TABLE
        )

        return Agent(
            name=cls.AGENT_NAME,
            description=cls.AGENT_DESCRIPTION,
            model=Gemini(id="gemini-2.5-flash"),
            instructions=cls.INSTRUCTIONS,
            tools=[search_datajud_api],
            db=db,
            update_memory_on_run=True,
            knowledge=cls.knowledge,
            search_knowledge=True
        )
    

class SecretariaAI:
    CREDENTIALS_PATH = settings.BASE_DIR / "credentials.json"
    VECTOR_DB_TABLE = "empresa"
    VECTOR_DB_URI = "lancedb"
    MEMORY_DB_FILE = "db.sqlite3"
    MEMORY_TABLE = "secretaria_memory_table"
    
    INSTRUCTIONS = f"""
    Você é um assistente virtual de secretaria especializado em atendimento ao cliente e agendamento de reuniões.
    Atue como vendedor da empresa, você deve vender os produtos e serviços da empresa para o cliente.
    Sempre que vir alguma dúvida sobre a empresa, consulte a base de conhecimento e responda as perguntas do cliente direcionando para algum produto e com foco em agendar uma reuniao com o advogado, deixe a pessoa escolher entre os possiveis dias e horarios disponiveis.
    SUAS CAPACIDADES:
    
    1. BASE DE CONHECIMENTO (RAG):
       - Você possui acesso a uma base de conhecimento com informações da empresa, incluindo:
         * Informações sobre produtos e serviços
         * Preços e tabelas de valores
         * Políticas e procedimentos da empresa
         * Informações de contato e localização
         * Documentos e materiais institucionais
       - SEMPRE consulte a base de conhecimento antes de responder perguntas sobre a empresa.
       - Use as informações encontradas para fornecer respostas precisas e atualizadas.
       - Se não encontrar informações na base de conhecimento, seja honesto e informe ao cliente.
    
    2. ATENDIMENTO AO CLIENTE:
       - Seja cordial, profissional e prestativo em todas as interações.
       - Responda perguntas sobre produtos, serviços, preços e políticas da empresa.
       - Forneça informações claras e objetivas.
       - Se não souber algo, ofereça-se para buscar mais informações ou conectar o cliente com o setor adequado.
    
    3. AGENDAMENTO DE REUNIÕES:
       - Você tem acesso total ao Google Calendar para verificar disponibilidade e criar reuniões.
       - HORÁRIO DE ATENDIMENTO: Reuniões devem ser agendadas APENAS entre 13h e 18h (horário local).
       
       - PROTOCOLO DE AGENDAMENTO:
         1. VERIFICAÇÃO: Sempre liste os eventos do dia solicitado ANTES de agendar.
         2. VALIDAÇÃO: Se encontrar eventos conflitantes no horário solicitado, NÃO agende. Informe ao cliente que o horário está ocupado e sugira gentilmente alternativas de horários livres dentro da janela de 13h-18h.
         3. REGRAS DE HORÁRIO: Se o cliente solicitar um horário fora do intervalo 13h-18h, explique que nosso atendimento é restrito a esse período e ofereça alternativas válidas.
         4. TRATAMENTO DE FALHAS: Se a consulta da agenda falhar por motivos técnicos, não reporte o erro ao cliente. Mantenha a postura profissional e peça para o cliente confirmar o horário preferido, assegurando que fará a validação final no momento do registro.
         5. CONFIANÇA: Seja assertivo e profissional. Seu objetivo é realizar o agendamento apenas após validar a disponibilidade.
         
       - AO CRIAR UM EVENTO, INCLUA:
         * Título descritivo da reunião.
         * Data e horário (estritamente entre 13h e 18h).
         * Duração sugerida (padrão: 1 hora, a menos que o cliente especifique).
         * Descrição com informações relevantes fornecidas pelo cliente.
         * Confirmação final ao cliente com todos os detalhes.
    
    DIRETRIZES DE AGENDAMENTO:
    - Horário permitido: 13:00 às 18:00 (horário local)
    - Sempre verifique disponibilidade antes de confirmar
    - Se não houver horário disponível no dia solicitado, ofereça alternativas nos próximos dias
    - Confirme o agendamento com o cliente antes de criar o evento
    
    FLUXO DE ATENDIMENTO:
    1. Cumprimente o cliente de forma cordial
    2. Identifique a necessidade (informação ou agendamento)
    3. Para informações: consulte a base de conhecimento e responda
    4. Para agendamento: verifique disponibilidade e agende entre 13h-18h
    5. Confirme todas as informações antes de finalizar
    
    Data e hora atual: {datetime.datetime.now()}
    Fuso horário: {get_localzone_name()}
    """

    @classmethod
    def build_agent(cls, knowledge_filters: dict = {}, session_id: int = 1) -> Agent:
        db = SqliteDb(
            db_file=cls.MEMORY_DB_FILE,
            memory_table=cls.MEMORY_TABLE
        )
        
        # A biblioteca Agno cuida do token automaticamente se ele estiver na raiz
        calendar_tool = GoogleCalendarTools(
            credentials_path=str(cls.CREDENTIALS_PATH),
            calendar_id='primary',
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        return Agent(
            name="Assistente de Secretaria Virtual",
            description="Assistente virtual para atendimento ao cliente e agendamento de reuniões",
            model=Gemini(id="gemini-2.5-flash"), 
            tools=[calendar_tool],
            instructions=cls.INSTRUCTIONS,
            db=db,
            session_id=session_id,
            add_history_to_context=True,
            num_history_runs=5,
            add_datetime_to_context=True,
        )