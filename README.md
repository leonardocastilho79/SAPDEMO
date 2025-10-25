# SAP RAG System

Sistema de Retrieval Augmented Generation (RAG) para documentos SAP, permitindo fazer perguntas em linguagem natural sobre documentação SAP e obter respostas contextualizadas.

## Sobre o Projeto

Este projeto implementa um sistema RAG completo que:

- Processa documentos SAP (PDF, DOCX)
- Cria embeddings vetoriais usando modelos multilíngues
- Armazena em banco de dados vetorial (ChromaDB ou FAISS)
- Permite consultas em linguagem natural
- Retorna respostas contextualizadas baseadas nos documentos

## Arquitetura

```
SAPDEMO/
├── src/
│   ├── document_processor/    # Processamento e chunking de documentos
│   ├── embeddings/            # Geração de embeddings vetoriais
│   ├── vector_store/          # Armazenamento vetorial (Chroma/FAISS)
│   └── rag_engine/            # Motor RAG principal
├── data/
│   ├── documents/             # Documentos SAP originais
│   ├── processed/             # Documentos processados
│   ├── chroma_db/            # Banco de dados ChromaDB
│   └── faiss_db/             # Índice FAISS
├── config/                    # Arquivos de configuração
├── notebooks/                 # Jupyter notebooks de exemplo
├── main.py                    # Script principal
└── requirements.txt           # Dependências
```

## Instalação

### 1. Clone o repositório

```bash
git clone <repository-url>
cd SAPDEMO
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente (opcional)

```bash
cp .env.example .env
# Edite .env se necessário
```

## Uso

### 1. Indexar Documentos

Primeiro, você precisa processar e indexar seus documentos SAP:

```bash
python main.py --mode ingest --documents ./data/documents
```

Opções disponíveis:
- `--vector-store`: Tipo de vector store (`chroma` ou `faiss`)
- `--chunk-size`: Tamanho dos chunks de texto (padrão: 1000)

Exemplo com FAISS:
```bash
python main.py --mode ingest --documents ./data/documents --vector-store faiss
```

### 2. Fazer Consultas

#### Modo Interativo

Execute o modo interativo para fazer múltiplas perguntas:

```bash
python main.py --mode interactive
```

Exemplo de sessão:
```
SAP RAG System - Modo Interativo
================================================================
Digite suas perguntas sobre os documentos SAP.
Digite 'sair' ou 'quit' para encerrar.

Sua pergunta: O que é SAP S/4HANA?

RESPOSTA:
================================================================
Encontrei as seguintes informações relevantes nos documentos SAP:

1. De 'Dominando o S4Hana.pdf' (relevância: 87.45%):
SAP S/4HANA é a suíte de aplicativos empresariais de próxima geração da SAP...
```

#### Consulta Única

Faça uma única pergunta:

```bash
python main.py --mode query --question "O que é SAP FIORI?"
```

### 3. Ver Estatísticas

Visualize estatísticas do sistema:

```bash
python main.py --mode stats
```

## Uso Programático

Você também pode usar o sistema em seu próprio código Python:

```python
from src.rag_engine import SAPRAGSystem

# Inicializar o sistema
rag = SAPRAGSystem(
    vector_store_type="chroma",
    chunk_size=1000
)

# Indexar documentos
result = rag.ingest_documents("./data/documents")
print(f"Indexados {result['stats']['total_chunks']} chunks")

# Fazer uma pergunta
answer = rag.answer_question("O que é SAP S/4HANA?", top_k=3)
print(answer['answer'])

# Ver fontes
for source in answer['sources']:
    print(f"- {source['metadata']['filename']}: {source['score']:.2%}")
```

## Exemplos de Perguntas

Aqui estão alguns exemplos de perguntas que você pode fazer:

- "O que é SAP S/4HANA?"
- "Quais são os principais módulos do SAP?"
- "Como funciona a integração FIORI?"
- "Explique o conceito de tabelas transparentes no SAP"
- "Quais são as diferenças entre SAP ECC e S/4HANA?"

## Componentes Principais

### 1. Document Processor

Processa documentos e os divide em chunks:

```python
from src.document_processor import DocumentProcessor

processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
chunks = processor.process_document("documento.pdf")
```

### 2. Embeddings Generator

Gera embeddings vetoriais para textos:

```python
from src.embeddings import EmbeddingsGenerator

generator = EmbeddingsGenerator()
embedding = generator.generate_embedding("Texto exemplo")
```

### 3. Vector Store

Armazena e recupera vetores:

```python
from src.vector_store import ChromaVectorStore

store = ChromaVectorStore()
store.add_documents(chunks, embeddings)
results = store.query(query_embedding, top_k=5)
```

## Configuração Avançada

### Modelos de Embeddings

O sistema usa por padrão o modelo multilíngue `paraphrase-multilingual-mpnet-base-v2`.

Você pode alterar para outros modelos editando `config/config.yaml`:

```yaml
embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
```

Modelos disponíveis:
- `paraphrase-multilingual-mpnet-base-v2` - Multilíngue (Português/Inglês)
- `all-MiniLM-L6-v2` - Rápido, apenas inglês
- `multi-qa-mpnet-base-dot-v1` - Otimizado para Q&A

### Vector Stores

#### ChromaDB (Padrão)
- Persistente
- Suporta filtros de metadados
- Fácil de usar

#### FAISS
- Mais rápido para grandes volumes
- Menor uso de memória
- Requer save/load manual

### Integração com LLM (Opcional)

Para gerar respostas mais elaboradas usando LLMs:

1. Configure sua API key no `.env`:
```bash
OPENAI_API_KEY=your_key_here
```

2. Modifique o código para usar `_generate_llm_answer`

## Estrutura dos Dados

### Formato de Chunks

Cada chunk processado contém:

```python
{
    'text': 'Texto do chunk...',
    'metadata': {
        'source': '/path/to/document.pdf',
        'filename': 'document.pdf',
        'chunk_index': 0,
        'total_chunks': 10,
        'type': 'pdf'
    }
}
```

### Resultados de Consulta

```python
{
    'question': 'Pergunta feita',
    'answer': 'Resposta gerada',
    'sources': [
        {
            'id': 'doc_0',
            'text': 'Texto relevante...',
            'metadata': {...},
            'score': 0.87
        }
    ],
    'context': 'Contexto completo...'
}
```

## Performance

### Benchmark

Com o dataset de exemplo (Dominando o S4Hana.pdf):

- Processamento: ~2-3 minutos
- Chunks gerados: ~500-1000
- Tempo de consulta: <1 segundo
- Memória: ~500MB-1GB (dependendo do modelo)

### Otimizações

1. **Chunk Size**: Diminua para 500 para respostas mais precisas
2. **Top K**: Aumente para 10 para mais contexto
3. **Vector Store**: Use FAISS para datasets grandes (>10k documentos)

## Limitações

- Suporta apenas PDF e DOCX
- Modelo multilíngue funciona melhor com Português e Inglês
- Sem geração de resposta com LLM por padrão (apenas contexto)

## Roadmap

- [ ] Suporte para mais formatos (TXT, HTML, MD)
- [ ] Integração nativa com OpenAI/Anthropic
- [ ] Interface Web (Gradio/Streamlit)
- [ ] Cache de embeddings
- [ ] Suporte a imagens em documentos
- [ ] API REST
- [ ] Docker support

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Troubleshooting

### Erro ao carregar modelo

```bash
# Limpe o cache e reinstale
pip uninstall sentence-transformers
pip install sentence-transformers
```

### ChromaDB não persiste

Verifique permissões do diretório:
```bash
chmod -R 755 data/chroma_db
```

### Memória insuficiente

Use um modelo menor:
```python
rag = SAPRAGSystem(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)
```

## Licença

MIT License - veja LICENSE para detalhes

## Contato

Para dúvidas e sugestões, abra uma issue no GitHub.

## Agradecimentos

- [LangChain](https://langchain.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
