"""
Implementação de vector store usando ChromaDB
"""

import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Armazena e recupera vetores usando ChromaDB"""

    def __init__(self, collection_name: str = "sap_documents", persist_directory: str = "./data/chroma_db"):
        """
        Inicializa o ChromaDB vector store

        Args:
            collection_name: Nome da coleção
            persist_directory: Diretório para persistir os dados
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Inicializando ChromaDB em: {persist_directory}")

        # Criar cliente ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )

        # Obter ou criar coleção
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Coleção '{collection_name}' carregada")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Nova coleção '{collection_name}' criada")

    def add_documents(self, chunks: List[Dict], embeddings: np.ndarray) -> None:
        """
        Adiciona documentos ao vector store

        Args:
            chunks: Lista de chunks com texto e metadados
            embeddings: Array de embeddings correspondentes
        """
        logger.info(f"Adicionando {len(chunks)} documentos ao ChromaDB")

        try:
            # Preparar dados
            ids = [f"doc_{i}" for i in range(len(chunks))]
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            embeddings_list = embeddings.tolist()

            # Adicionar à coleção em batches
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                end_idx = min(i + batch_size, len(chunks))

                self.collection.add(
                    ids=ids[i:end_idx],
                    embeddings=embeddings_list[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx]
                )

            logger.info(f"Documentos adicionados com sucesso")

        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {str(e)}")
            raise

    def query(self, query_embedding: np.ndarray, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Consulta documentos similares

        Args:
            query_embedding: Embedding da consulta
            top_k: Número de resultados a retornar
            filter_metadata: Filtros de metadados opcionais

        Returns:
            Lista de documentos relevantes com scores
        """
        try:
            results = self.collection.query(
                query_embeddings=query_embedding.reshape(1, -1).tolist(),
                n_results=top_k,
                where=filter_metadata
            )

            # Formatar resultados
            documents = []
            for i in range(len(results['ids'][0])):
                doc = {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'score': 1 - results['distances'][0][i] if 'distances' in results else None
                }
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Erro ao consultar documentos: {str(e)}")
            raise

    def delete_collection(self) -> None:
        """Remove a coleção"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Coleção '{self.collection_name}' removida")
        except Exception as e:
            logger.error(f"Erro ao remover coleção: {str(e)}")
            raise

    def get_stats(self) -> Dict:
        """Retorna estatísticas da coleção"""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'document_count': count,
            'persist_directory': str(self.persist_directory)
        }

    def reset(self) -> None:
        """Limpa todos os documentos da coleção"""
        try:
            # Deletar e recriar coleção
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Coleção '{self.collection_name}' resetada")
        except Exception as e:
            logger.error(f"Erro ao resetar coleção: {str(e)}")
            raise
