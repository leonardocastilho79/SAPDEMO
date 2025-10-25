"""
Gerador de embeddings usando modelos de linguagem
"""

import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Gera embeddings vetoriais para textos usando Sentence Transformers"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"):
        """
        Inicializa o gerador de embeddings

        Args:
            model_name: Nome do modelo do Sentence Transformers a ser usado
                       (padrão: modelo multilíngue que suporta português)
        """
        logger.info(f"Carregando modelo de embeddings: {model_name}")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Modelo carregado. Dimensão dos embeddings: {self.embedding_dim}")

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Gera embedding para um único texto

        Args:
            text: Texto para gerar embedding

        Returns:
            Array numpy com o vetor de embedding
        """
        if not text or not text.strip():
            logger.warning("Texto vazio fornecido, retornando vetor zero")
            return np.zeros(self.embedding_dim)

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            raise

    def generate_embeddings(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        Gera embeddings para uma lista de textos

        Args:
            texts: Lista de textos
            batch_size: Tamanho do batch para processamento
            show_progress: Se deve mostrar barra de progresso

        Returns:
            Array numpy com os vetores de embedding
        """
        if not texts:
            logger.warning("Lista de textos vazia")
            return np.array([])

        logger.info(f"Gerando embeddings para {len(texts)} textos")

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            logger.info(f"Embeddings gerados com sucesso. Shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Erro ao gerar embeddings em lote: {str(e)}")
            raise

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula a similaridade de cosseno entre dois textos

        Args:
            text1: Primeiro texto
            text2: Segundo texto

        Returns:
            Similaridade entre 0 e 1
        """
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)

        # Similaridade de cosseno
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)

    def get_model_info(self) -> dict:
        """
        Retorna informações sobre o modelo de embeddings

        Returns:
            Dicionário com informações do modelo
        """
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'max_sequence_length': self.model.max_seq_length
        }


class OpenAIEmbeddingsGenerator:
    """
    Gerador de embeddings usando OpenAI API (alternativa)
    Requer configuração de API key
    """

    def __init__(self, api_key: str = None, model: str = "text-embedding-ada-002"):
        """
        Inicializa o gerador de embeddings OpenAI

        Args:
            api_key: Chave da API OpenAI
            model: Modelo de embeddings a usar
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai não está instalado. Instale com: pip install openai")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"OpenAI Embeddings inicializado com modelo: {model}")

    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenAI API"""
        if not text or not text.strip():
            logger.warning("Texto vazio fornecido")
            return []

        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding com OpenAI: {str(e)}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos"""
        embeddings = []
        for text in texts:
            emb = self.generate_embedding(text)
            embeddings.append(emb)
        return embeddings
