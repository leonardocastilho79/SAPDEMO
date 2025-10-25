"""
Script principal para executar o SAP RAG System
"""

import argparse
import logging
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_engine import SAPRAGSystem

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sap_rag.log')
    ]
)

logger = logging.getLogger(__name__)


def ingest_documents(rag_system: SAPRAGSystem, documents_path: str):
    """Ingere documentos no sistema RAG"""
    logger.info(f"Iniciando ingestão de documentos de: {documents_path}")

    result = rag_system.ingest_documents(documents_path)

    if result['status'] == 'success':
        stats = result['stats']
        print("\n" + "="*60)
        print("DOCUMENTOS INDEXADOS COM SUCESSO!")
        print("="*60)
        print(f"Total de chunks: {stats['total_chunks']}")
        print(f"Total de caracteres: {stats['total_characters']}")
        print(f"Tamanho médio do chunk: {stats['avg_chunk_size']}")
        print(f"Documentos processados: {stats['unique_sources']}")
        print("\nFontes:")
        for source in stats['sources']:
            print(f"  - {Path(source).name}")
        print("="*60)
    else:
        print(f"Erro: {result.get('message', 'Erro desconhecido')}")


def query_interactive(rag_system: SAPRAGSystem):
    """Modo interativo de consulta"""
    print("\n" + "="*60)
    print("SAP RAG System - Modo Interativo")
    print("="*60)
    print("Digite suas perguntas sobre os documentos SAP.")
    print("Digite 'sair' ou 'quit' para encerrar.\n")

    while True:
        try:
            question = input("\nSua pergunta: ").strip()

            if question.lower() in ['sair', 'quit', 'exit']:
                print("\nEncerrando...")
                break

            if not question:
                continue

            print("\nBuscando informações relevantes...")

            result = rag_system.answer_question(question, top_k=3)

            print("\n" + "-"*60)
            print("RESPOSTA:")
            print("-"*60)
            print(result['answer'])
            print("\n" + "-"*60)
            print(f"Fontes consultadas: {len(result['sources'])}")
            print("-"*60)

        except KeyboardInterrupt:
            print("\n\nEncerrando...")
            break
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            print(f"\nErro ao processar pergunta: {e}")


def query_single(rag_system: SAPRAGSystem, question: str):
    """Faz uma única consulta"""
    logger.info(f"Processando consulta: {question}")

    result = rag_system.answer_question(question, top_k=3)

    print("\n" + "="*60)
    print("PERGUNTA:")
    print("="*60)
    print(question)
    print("\n" + "="*60)
    print("RESPOSTA:")
    print("="*60)
    print(result['answer'])
    print("\n" + "="*60)
    print("FONTES:")
    print("="*60)

    for i, source in enumerate(result['sources'], 1):
        filename = source['metadata'].get('filename', 'Unknown')
        score = source.get('score', 0)
        print(f"\n{i}. {filename} (Relevância: {score:.2%})")
        print(f"   {source['text'][:200]}...")

    print("="*60)


def show_stats(rag_system: SAPRAGSystem):
    """Mostra estatísticas do sistema"""
    stats = rag_system.get_system_stats()

    print("\n" + "="*60)
    print("ESTATÍSTICAS DO SISTEMA")
    print("="*60)

    print("\nVector Store:")
    for key, value in stats['vector_store'].items():
        print(f"  {key}: {value}")

    print("\nModelo de Embeddings:")
    for key, value in stats['embedding_model'].items():
        print(f"  {key}: {value}")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='SAP RAG System - Sistema de Retrieval Augmented Generation para documentos SAP'
    )

    parser.add_argument(
        '--mode',
        choices=['ingest', 'query', 'interactive', 'stats'],
        required=True,
        help='Modo de operação'
    )

    parser.add_argument(
        '--documents',
        type=str,
        help='Caminho para o diretório com documentos (modo ingest)'
    )

    parser.add_argument(
        '--question',
        type=str,
        help='Pergunta para fazer ao sistema (modo query)'
    )

    parser.add_argument(
        '--vector-store',
        choices=['chroma', 'faiss'],
        default='chroma',
        help='Tipo de vector store a usar (padrão: chroma)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Tamanho dos chunks de texto (padrão: 1000)'
    )

    args = parser.parse_args()

    # Inicializar sistema RAG
    logger.info("Inicializando SAP RAG System...")

    rag_system = SAPRAGSystem(
        vector_store_type=args.vector_store,
        chunk_size=args.chunk_size
    )

    # Executar modo selecionado
    if args.mode == 'ingest':
        if not args.documents:
            parser.error("--documents é obrigatório no modo ingest")
        ingest_documents(rag_system, args.documents)

    elif args.mode == 'query':
        if not args.question:
            parser.error("--question é obrigatório no modo query")
        query_single(rag_system, args.question)

    elif args.mode == 'interactive':
        query_interactive(rag_system)

    elif args.mode == 'stats':
        show_stats(rag_system)


if __name__ == "__main__":
    main()
