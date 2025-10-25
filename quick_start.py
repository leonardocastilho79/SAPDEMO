#!/usr/bin/env python3
"""
Script de início rápido para testar o SAP RAG System
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_engine import SAPRAGSystem


def main():
    print("=" * 60)
    print("SAP RAG System - Quick Start")
    print("=" * 60)

    # Inicializar sistema
    print("\n1. Inicializando sistema RAG...")
    rag = SAPRAGSystem(vector_store_type="chroma")
    print("   Sistema inicializado!")

    # Verificar se há documentos indexados
    stats = rag.get_system_stats()
    doc_count = stats['vector_store'].get('document_count', 0)

    if doc_count == 0:
        print("\n2. Nenhum documento indexado encontrado.")
        print("   Indexando documentos de ./data/documents...")

        result = rag.ingest_documents("./data/documents")

        if result['status'] == 'success':
            print(f"   ✓ {result['stats']['total_chunks']} chunks indexados!")
        else:
            print(f"   ✗ Erro: {result.get('message')}")
            return
    else:
        print(f"\n2. Sistema já possui {doc_count} documentos indexados.")

    # Fazer perguntas de exemplo
    print("\n3. Fazendo perguntas de exemplo...\n")

    perguntas = [
        "O que é SAP S/4HANA?",
        "Quais são os principais módulos do SAP?",
    ]

    for i, pergunta in enumerate(perguntas, 1):
        print(f"\nPergunta {i}: {pergunta}")
        print("-" * 60)

        resultado = rag.answer_question(pergunta, top_k=2)

        # Mostrar apenas primeira fonte
        if resultado['sources']:
            fonte = resultado['sources'][0]
            print(f"Fonte: {fonte['metadata']['filename']}")
            print(f"Relevância: {fonte.get('score', 0):.2%}")
            print(f"\nTrecho: {fonte['text'][:300]}...")

        print("-" * 60)

    print("\n" + "=" * 60)
    print("Quick Start concluído!")
    print("\nPróximos passos:")
    print("1. Execute: python main.py --mode interactive")
    print("2. Ou abra o notebook: notebooks/exemplo_sap_rag.ipynb")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
