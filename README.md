# ⚖️ JuriIA - Assistente Jurídico com Agentes Autônomos

O **JuriIA** é uma solução de automação jurídica inteligente desenvolvida para otimizar o atendimento ao cliente e a gestão de processos. O sistema utiliza Inteligência Artificial (LLMs) com a metodologia **RAG (Retrieval-Augmented Generation)** para fornecer respostas precisas sobre a empresa e **Agentes Autônomos** para interagir com ferramentas externas, como o Google Calendar.

---

## 🚀 Principais Funcionalidades

* **Atendimento Jurídico Inteligente**: Responde dúvidas sobre produtos, serviços e políticas com base em documentos da empresa (RAG).
* **Agendamento Autônomo**: Integração nativa com o Google Calendar para verificar disponibilidade e criar reuniões de forma assertiva entre 13h e 18h.
* **Consulta Processual**: Busca automatizada de dados de processos judiciais na API pública do **DataJud (CNJ)**.
* **Arquitetura Resiliente**: Implementado com memória persistente de sessões e protocolos de segurança para evitar falhas técnicas no atendimento.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem**: Python 3.12.6 (Recomendamos o uso de um ambiente virtual (venv) para isolar as dependências)
* **Framework**: Django
* **IA & Agentes**: Agno (Agentes com Tools) & Google Gemini (LLM)
* **Vetorização (RAG)**: LanceDB & Gemini Embeddings
* **APIs**: Google Calendar API & DataJud (CNJ)

---

## 📋 Como Instalar e Rodar

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/seu-usuario/projeto_juri_ia.git](https://github.com/seu-usuario/projeto_juri_ia.git)
   cd projeto_juri_ia
2. **Crie e ative o ambiente virtual:**
  
  Bash
  python -m venv venv
  source venv/bin/activate  # No Windows: venv\Scripts\activate
  Instale as dependências:
  
  Bash
  pip install -r requirements.txt
  Configure as variáveis de ambiente:
  Crie um arquivo .env na raiz do projeto e adicione suas chaves (Google API, etc).
  
 3. **Execute o servidor:**
  
  Bash
  python manage.py runserver
## 🏗️ Arquitetura do Sistema
  O sistema foi desenhado para separar a camada de conhecimento (documentos) da camada de execução (agentes), garantindo que a IA consulte sempre a base de dados antes de realizar qualquer ação externa.
  
## 📝 Licença
  Este projeto está sob a licença MIT. Sinta-se à vontade para utilizar, aprender e contribuir!
