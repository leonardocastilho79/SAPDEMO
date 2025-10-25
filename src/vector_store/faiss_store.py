"""
Implementação de vector store usando FAISS
"""

import logging
from typing import List, Dict, Optional
import numpy as np
import faiss
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """Armazena e recupera vetores usando FAISS"""

    def __init__(self, embedding_dim: int = 768, persist_directory: str = "./data/faiss_db"):
        """
        Inicializa o FAISS vector store

        Args:
            embedding_dim: Dimensão dos vetores de embedding
            persist_directory: Diretório para persistir o índice
        """
        self.embedding_dim = embedding_dim
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.index_path = self.persist_directory / "faiss_index.bin"
        self.metadata_path = self.persist_directory / "metadata.pkl"

        logger.info(f"Inicializando FAISS com dimensão: {embedding_dim}")

        # Criar ou carregar índice FAISS
        if self.index_path.exists():
            self.load_index()
        else:
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.documents = []
            self.metadatas = []
            logger.info("Novo índice FAISS criado")

    def add_documents(self, chunks: List[Dict], embeddings: np.ndarray) -> None:
        """
        Adiciona documentos ao vector store

        Args:
            chunks: Lista de chunks com texto e metadados
            embeddings: Array de embeddings correspondentes
        """
        logger.info(f"Adicionando {len(chunks)} documentos ao FAISS")

        try:
            # Normalizar embeddings para busca por similaridade de cosseno
            embeddings_normalized = embeddings.astype('float32')

            # Adicionar ao índice
            self.index.add(embeddings_normalized)

            # Armazenar documentos e metadados
            for chunk in chunks:
                self.documents.append(chunk['text'])
                self.metadatas.append(chunk['metadata'])

            logger.info(f"Total de documentos no índice: {self.index.ntotal}")

        except Exception as e:
            logger.error(f"Erro ao adicionar documentos ao FAISS: {str(e)}")
            raise

    def query(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Consulta documentos similares

        Args:
            query_embedding: Embedding da consulta
            top_k: Número de resultados a retornar

        Returns:
            Lista de documentos relevantes com scores
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Índice vazio")
                return []

            # Normalizar query embedding
            query_normalized = query_embedding.astype('float32').reshape(1, -1)

            # Buscar k vizinhos mais próximos
            distances, indices = self.index.search(query_normalized, top_k)

            # Formatar resultados
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    # Converter distância L2 para score de similaridade
                    score = 1 / (1 + distance)

                    result = {
                        'id': f"doc_{idx}",
                        'text': self.documents[idx],
                        'metadata': self.metadatas[idx],
                        'distance': float(distance),
                        'score': float(score)
                    }
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Erro ao consultar FAISS: {str(e)}")
            raise

    def save_index(self) -> None:
        """Salva o índice FAISS e metadados em disco"""
        try:
            logger.info(f"Salvando índice FAISS em: {self.index_path}")

            # Salvar índice FAISS
            faiss.write_index(self.index, str(self.index_path))

            # Salvar metadados
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadatas': self.metadatas
                }, f)

            logger.info("Índice FAISS salvo com sucesso")

        except Exception as e:
            logger.error(f"Erro ao salvar índice FAISS: {str(e)}")
            raise

    def load_index(self) -> None:
        """Carrega o índice FAISS e metadados do disco"""
        try:
            logger.info(f"Carregando índice FAISS de: {self.index_path}")

            # Carregar índice FAISS
            self.index = faiss.read_index(str(self.index_path))

            # Carregar metadados
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadatas = data['metadatas']

            logger.info(f"Índice FAISS carregado. Total de documentos: {self.index.ntotal}")

        except Exception as e:
            logger.error(f"Erro ao carregar índice FAISS: {str(e)}")
            raise

    def get_stats(self) -> Dict:
        """Retorna estatísticas do índice"""
        return {
            'index_type': 'FAISS',
            'document_count': self.index.ntotal,
            'embedding_dimension': self.embedding_dim,
            'persist_directory': str(self.persist_directory)
        }

    def reset(self) -> None:
        """Limpa o índice"""
        try:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.documents = []
            self.metadatas = []
            logger.info("Índice FAISS resetado")
        except Exception as e:
            logger.error(f"Erro ao resetar índice FAISS: {str(e)}")
            raise
