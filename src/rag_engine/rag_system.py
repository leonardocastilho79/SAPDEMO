"""
Sistema RAG completo para documentos SAP
"""

import logging
from typing import List, Dict, Optional
import os
from pathlib import Path

from ..document_processor import DocumentProcessor
from ..embeddings import EmbeddingsGenerator
from ..vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class SAPRAGSystem:
    """Sistema completo de RAG para documentos SAP"""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        vector_store_type: str = "chroma",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_directory: str = "./data"
    ):
        """
        Inicializa o sistema RAG

        Args:
            embedding_model: Modelo para gerar embeddings
            vector_store_type: Tipo de vector store ('chroma' ou 'faiss')
            chunk_size: Tamanho dos chunks de texto
            chunk_overlap: Sobreposição entre chunks
            persist_directory: Diretório para persistir dados
        """
        logger.info("Inicializando SAP RAG System")

        # Inicializar componentes
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.embeddings_generator = EmbeddingsGenerator(model_name=embedding_model)

        # Inicializar vector store
        if vector_store_type == "chroma":
            self.vector_store = ChromaVectorStore(
                persist_directory=os.path.join(persist_directory, "chroma_db")
            )
        else:
            from ..vector_store import FAISSVectorStore
            self.vector_store = FAISSVectorStore(
                embedding_dim=self.embeddings_generator.embedding_dim,
                persist_directory=os.path.join(persist_directory, "faiss_db")
            )

        self.vector_store_type = vector_store_type
        logger.info(f"SAP RAG System inicializado com vector store: {vector_store_type}")

    def ingest_documents(self, directory_path: str) -> Dict:
        """
        Processa e indexa todos os documentos de um diretório

        Args:
            directory_path: Caminho para o diretório com documentos

        Returns:
            Estatísticas do processamento
        """
        logger.info(f"Iniciando ingestão de documentos de: {directory_path}")

        # Processar documentos
        chunks = self.document_processor.process_directory(directory_path)

        if not chunks:
            logger.warning("Nenhum documento encontrado para processar")
            return {'status': 'error', 'message': 'Nenhum documento encontrado'}

        # Gerar embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embeddings_generator.generate_embeddings(texts)

        # Adicionar ao vector store
        self.vector_store.add_documents(chunks, embeddings)

        # Salvar índice se for FAISS
        if self.vector_store_type == "faiss":
            self.vector_store.save_index()

        # Retornar estatísticas
        stats = self.document_processor.get_document_stats(chunks)
        stats['vector_store_stats'] = self.vector_store.get_stats()

        logger.info(f"Ingestão concluída: {stats['total_chunks']} chunks indexados")

        return {
            'status': 'success',
            'stats': stats
        }

    def ingest_single_document(self, file_path: str) -> Dict:
        """
        Processa e indexa um único documento

        Args:
            file_path: Caminho para o arquivo

        Returns:
            Estatísticas do processamento
        """
        logger.info(f"Iniciando ingestão de documento: {file_path}")

        # Processar documento
        chunks = self.document_processor.process_document(file_path)

        # Gerar embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embeddings_generator.generate_embeddings(texts)

        # Adicionar ao vector store
        self.vector_store.add_documents(chunks, embeddings)

        # Salvar índice se for FAISS
        if self.vector_store_type == "faiss":
            self.vector_store.save_index()

        stats = self.document_processor.get_document_stats(chunks)

        logger.info(f"Documento indexado: {stats['total_chunks']} chunks")

        return {
            'status': 'success',
            'stats': stats
        }

    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        Faz uma consulta ao sistema RAG

        Args:
            question: Pergunta do usuário
            top_k: Número de documentos relevantes a retornar

        Returns:
            Dicionário com contexto relevante e metadados
        """
        logger.info(f"Processando consulta: {question}")

        # Gerar embedding da pergunta
        query_embedding = self.embeddings_generator.generate_embedding(question)

        # Buscar documentos relevantes
        relevant_docs = self.vector_store.query(query_embedding, top_k=top_k)

        # Construir contexto
        context = self._build_context(relevant_docs)

        return {
            'question': question,
            'context': context,
            'relevant_documents': relevant_docs,
            'num_sources': len(relevant_docs)
        }

    def answer_question(self, question: str, top_k: int = 5, use_llm: bool = False) -> Dict:
        """
        Responde uma pergunta usando RAG

        Args:
            question: Pergunta do usuário
            top_k: Número de documentos a recuperar
            use_llm: Se deve usar LLM para gerar resposta (requer configuração)

        Returns:
            Resposta e contexto
        """
        # Obter contexto relevante
        query_result = self.query(question, top_k)

        if use_llm:
            # Gerar resposta usando LLM
            answer = self._generate_llm_answer(question, query_result['context'])
        else:
            # Retornar apenas o contexto
            answer = self._generate_simple_answer(query_result['relevant_documents'])

        return {
            'question': question,
            'answer': answer,
            'sources': query_result['relevant_documents'],
            'context': query_result['context']
        }

    def _build_context(self, documents: List[Dict]) -> str:
        """Constrói contexto a partir dos documentos recuperados"""
        context_parts = []

        for i, doc in enumerate(documents, 1):
            source = doc['metadata'].get('filename', 'Unknown')
            text = doc['text']
            context_parts.append(f"[Fonte {i}: {source}]\n{text}")

        return "\n\n".join(context_parts)

    def _generate_simple_answer(self, documents: List[Dict]) -> str:
        """Gera uma resposta simples baseada nos documentos recuperados"""
        if not documents:
            return "Desculpe, não encontrei informações relevantes sobre sua pergunta nos documentos SAP."

        # Retornar os trechos mais relevantes
        answer_parts = [
            "Encontrei as seguintes informações relevantes nos documentos SAP:\n"
        ]

        for i, doc in enumerate(documents[:3], 1):
            source = doc['metadata'].get('filename', 'Unknown')
            text = doc['text'][:300] + "..." if len(doc['text']) > 300 else doc['text']
            score = doc.get('score', 0)

            answer_parts.append(
                f"\n{i}. De '{source}' (relevância: {score:.2%}):\n{text}"
            )

        return "\n".join(answer_parts)

    def _generate_llm_answer(self, question: str, context: str) -> str:
        """
        Gera resposta usando LLM (requer configuração de API)

        Args:
            question: Pergunta do usuário
            context: Contexto recuperado

        Returns:
            Resposta gerada
        """
        # Placeholder para integração com LLM
        # Pode ser implementado com OpenAI, Anthropic, ou LLM local

        prompt = f"""Com base no contexto abaixo, responda a pergunta de forma clara e concisa.

Contexto:
{context}

Pergunta: {question}

Resposta:"""

        # Aqui você pode integrar com a API do LLM de sua escolha
        # Por enquanto, retornamos uma mensagem indicativa

        return "Integração com LLM não configurada. Use use_llm=False para ver o contexto recuperado."

    def get_system_stats(self) -> Dict:
        """Retorna estatísticas do sistema"""
        vector_stats = self.vector_store.get_stats()
        embedding_info = self.embeddings_generator.get_model_info()

        return {
            'vector_store': vector_stats,
            'embedding_model': embedding_info
        }

    def reset_index(self) -> None:
        """Limpa o índice vetorial"""
        logger.info("Resetando índice vetorial")
        self.vector_store.reset()
        logger.info("Índice resetado com sucesso")
