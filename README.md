# Agente Inteligente NovaShop — RAG com OCI Generative AI

Agente de IA para atendimento ao cliente de e-commerce, capaz de responder
perguntas com base em documentos reais da operação (FAQ, política de
reembolso/devolução e guia de envios). O agente usa **RAG (Retrieval-Augmented
Generation)**: busca os trechos mais relevantes dos documentos e usa um LLM
para gerar uma resposta em linguagem natural, sempre com base no conteúdo
recuperado — reduzindo alucinações e mantendo a resposta alinhada às políticas
reais da empresa.

Projeto desenvolvido para o Challenge Alura + Oracle "Agente Inteligente".

---

## Descrição geral

O agente lê documentos em PDF (ou CSV) contendo as políticas e o FAQ da loja
fictícia **NovaShop**, indexa esse conteúdo em um banco vetorial local e
expõe uma API HTTP (`POST /ask`) onde qualquer cliente pode enviar uma
pergunta em português e receber uma resposta contextualizada, junto com a
indicação de quais documentos foram usados como fonte.

Documentos usados como base de conhecimento (pasta `data/`):
- `FAQ_NovaShop.pdf` — perguntas frequentes sobre pedidos, pagamento e atendimento
- `Politica_Reembolso_Devolucoes_NovaShop.pdf` — regras de devolução e reembolso
- `Guia_Envios_Entregas_NovaShop.pdf` — prazos de entrega, frete e rastreamento

## Arquitetura da solução

```
                         ┌─────────────────────────┐
                         │   Documentos (PDF/CSV)   │
                         │         data/            │
                         └────────────┬─────────────┘
                                      │  scripts/build_index.py
                                      ▼
                         ┌─────────────────────────┐
                         │  1. Leitura + Chunking    │  app/document_loader.py
                         └────────────┬─────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │ 2. Embeddings (OCI GenAI) │  app/oci_genai_client.py
                         └────────────┬─────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │ 3. Índice vetorial FAISS  │  app/vector_store.py
                         │        index/             │
                         └────────────┬─────────────┘
                                      │
   Cliente ──POST /ask──▶ FastAPI ──▶ │ 4. Busca por similaridade
   (pergunta)             app/main.py│    (top-K chunks relevantes)
                                      ▼
                         ┌─────────────────────────┐
                         │ 5. Geração da resposta     │  app/oci_genai_client.py
                         │   (Chat model OCI GenAI)   │  app/rag_engine.py
                         └────────────┬─────────────┘
                                      ▼
   Cliente ◀──resposta + fontes────── FastAPI
```

**Fluxo resumido:**
1. Os documentos são lidos e divididos em pedaços (*chunks*) de ~800 caracteres com sobreposição.
2. Cada chunk vira um vetor numérico (*embedding*) via **OCI Generative AI — Embeddings**.
3. Os vetores são armazenados em um índice **FAISS** local, persistido em disco.
4. Quando o usuário pergunta algo, a pergunta também vira embedding e o FAISS retorna os chunks mais similares (busca por cosseno).
5. Os chunks recuperados + a pergunta são enviados ao modelo de chat da **OCI Generative AI**, que gera a resposta final em linguagem natural, restrita ao contexto fornecido.

## Tecnologias e ferramentas utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| API | FastAPI + Uvicorn |
| Leitura de PDF | pypdf |
| Embeddings e geração de texto | OCI Generative AI (`oci` SDK) |
| Banco vetorial | FAISS (faiss-cpu) |
| Testes | Pytest + FastAPI TestClient |
| Empacotamento | Docker |
| Deploy | OCI Container Instances *(ou OCI Data Science / OKE, ver seção de deploy)* |
| Versionamento | Git / GitHub |

## Estrutura do repositório

```
alura-agente-rag/
├── app/
│   ├── main.py              # API FastAPI (endpoints /health e /ask)
│   ├── config.py             # configurações via variáveis de ambiente
│   ├── document_loader.py    # leitura e chunking de PDF/CSV
│   ├── oci_genai_client.py   # integração com OCI Generative AI (embeddings + chat)
│   ├── vector_store.py       # índice vetorial FAISS
│   └── rag_engine.py         # orquestração do fluxo RAG
├── scripts/
│   └── build_index.py        # script de ingestão (roda antes da API subir)
├── data/                     # documentos fonte (PDFs da NovaShop)
├── tests/
│   └── test_api.py           # testes automatizados
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Instruções para executar o projeto

### 1. Pré-requisitos

- Python 3.11+
- Conta OCI com acesso liberado ao serviço **Generative AI** em uma região suportada
- Arquivo `~/.oci/config` configurado (siga o [guia oficial de configuração do SDK/CLI](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm))

### 2. Instalação local

```bash
git clone https://github.com/SEU-USUARIO/alura-agente-rag.git
cd alura-agente-rag

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edite o .env com o OCID do seu compartment, endpoint da região e IDs dos modelos
```

### 3. Construir o índice vetorial (ingestão dos documentos)

```bash
python scripts/build_index.py
```

Isso lê os PDFs em `data/`, gera os embeddings via OCI e salva o índice em `index/`.

### 4. Rodar a API localmente

```bash
uvicorn app.main:app --reload --port 8000
```

Acesse a documentação interativa em `http://localhost:8000/docs`.

### 5. Rodar os testes

```bash
pytest
```

### 6. Rodar via Docker

```bash
docker build -t agente-novashop .
docker run -p 8000:8000 --env-file .env agente-novashop
```

## Deploy na OCI

Sugestão de caminho mais simples para este projeto (container único, sem orquestração):

1. Faça login no **OCI Registry (OCIR)** e publique a imagem:
   ```bash
   docker build -t <regiao>.ocir.io/<namespace>/agente-novashop:v1 .
   docker push <regiao>.ocir.io/<namespace>/agente-novashop:v1
   ```
2. No console da OCI, crie um **Container Instance** apontando para essa imagem, configurando as variáveis de ambiente do `.env` diretamente no console (nunca commitar o `.env` real).
3. Libere a porta 8000 na regra de segurança (Security List / NSG) do VCN associado.
4. Anote o IP público / endpoint gerado — esse é o link a ser incluído como evidência de deploy.

> Alternativas: **OCI Data Science Model Deployment** (se preferir empacotar como modelo) ou usar diretamente o **OCI Generative AI Agents Service** (no-code), fazendo upload dos PDFs para um bucket do Object Storage — ver documentação oficial: https://docs.oracle.com/en-us/iaas/Content/generative-ai-agents/overview.htm

**Evidência do deploy:** _(preencher após publicar)_
- 🔗 URL pública: `https://SEU-ENDPOINT-AQUI`
- 📸 Captura de tela: adicionar `docs/print-deploy.png` e referenciar aqui

## Exemplos de perguntas que o agente consegue responder

- "Qual o prazo para devolver um produto que veio com defeito?"
- "Vocês entregam para a região Norte? Quanto tempo demora?"
- "Posso pagar no Pix? Tem desconto?"
- "Como faço para rastrear meu pedido?"
- "O frete é grátis a partir de qual valor de compra?"
- "Perdi o prazo de 7 dias, ainda posso devolver o produto?"

## Exemplos de respostas geradas pelo agente

**Pergunta:**
```json
{ "question": "Qual o prazo para devolver um produto que veio com defeito?" }
```

**Resposta:**
```json
{
  "answer": "Se o produto apresentar defeito de fabricação ou avaria de transporte, você deve comunicar a NovaShop em até 7 dias corridos após o recebimento (produtos não duráveis) ou até 90 dias corridos (produtos duráveis). É importante anexar fotos do problema ao abrir a solicitação em 'Meus Pedidos'.",
  "sources": ["Politica_Reembolso_Devolucoes_NovaShop.pdf"]
}
```

**Pergunta:**
```json
{ "question": "O frete é grátis a partir de qual valor?" }
```

**Resposta:**
```json
{
  "answer": "Pedidos acima de R$ 250,00 têm frete grátis via envio padrão para todo o território nacional. O valor do frete para pedidos abaixo desse valor é calculado automaticamente no carrinho, com base no CEP, peso e dimensões dos itens.",
  "sources": ["Guia_Envios_Entregas_NovaShop.pdf"]
}
```

> As respostas acima foram validadas manualmente com base no conteúdo dos documentos em `data/`. Ao rodar contra a OCI de verdade, o texto exato pode variar levemente conforme o modelo de chat utilizado.

## Testando via curl

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Como faço para rastrear meu pedido?"}'
```

## Limitações conhecidas / próximos passos

- O índice é reconstruído inteiramente a cada `build_index.py`; para bases maiores, vale migrar para atualização incremental.
- Não há autenticação na API — para produção, adicionar API key ou OAuth.
- Não há histórico de conversa (multi-turn); cada pergunta é tratada isoladamente.
- Poderia evoluir para usar o **OCI Generative AI Agents Service** gerenciado, delegando ingestão e retrieval à própria OCI.
