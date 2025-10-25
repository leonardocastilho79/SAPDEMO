"""
Processador principal de documentos
"""

import os
from typing import List, Dict
from pathlib import Path
import logging
from .loaders import LoaderFactory

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processa documentos e os divide em chunks para indexação"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa o processador de documentos

        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres
            chunk_overlap: Quantidade de caracteres que se sobrepõem entre chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, file_path: str) -> List[Dict]:
        """
        Processa um documento e retorna uma lista de chunks

        Args:
            file_path: Caminho para o arquivo

        Returns:
            Lista de dicionários contendo chunks de texto e metadados
        """
        logger.info(f"Processando documento: {file_path}")

        # Carregar documento usando o loader apropriado
        loader = LoaderFactory.get_loader(file_path)
        doc_data = loader.load()

        # Extrair texto baseado no tipo de documento
        full_text = self._extract_full_text(doc_data)

        # Dividir em chunks
        chunks = self._split_text(full_text)

        # Criar lista de chunks com metadados
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'text': chunk,
                'metadata': {
                    **doc_data['metadata'],
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            }
            processed_chunks.append(chunk_data)

        logger.info(f"Documento processado: {len(processed_chunks)} chunks criados")
        return processed_chunks

    def process_directory(self, directory_path: str) -> List[Dict]:
        """
        Processa todos os documentos suportados em um diretório

        Args:
            directory_path: Caminho para o diretório

        Returns:
            Lista de chunks de todos os documentos
        """
        logger.info(f"Processando diretório: {directory_path}")

        directory = Path(directory_path)
        all_chunks = []

        # Processar todos os arquivos suportados
        supported_extensions = ['.pdf', '.docx']

        for ext in supported_extensions:
            for file_path in directory.glob(f"*{ext}"):
                try:
                    chunks = self.process_document(str(file_path))
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {str(e)}")

        logger.info(f"Total de chunks processados: {len(all_chunks)}")
        return all_chunks

    def _extract_full_text(self, doc_data: Dict) -> str:
        """Extrai o texto completo dos dados do documento"""
        if 'pages' in doc_data:
            # Documento PDF
            return "\n\n".join([page['text'] for page in doc_data['pages']])
        elif 'paragraphs' in doc_data:
            # Documento DOCX
            return "\n\n".join([para['text'] for para in doc_data['paragraphs']])
        else:
            raise ValueError("Formato de documento não reconhecido")

    def _split_text(self, text: str) -> List[str]:
        """
        Divide o texto em chunks com sobreposição

        Args:
            text: Texto completo para dividir

        Returns:
            Lista de chunks de texto
        """
        chunks = []
        start = 0

        while start < len(text):
            # Definir fim do chunk
            end = start + self.chunk_size

            # Se não for o último chunk, tentar quebrar em uma sentença
            if end < len(text):
                # Procurar por quebra de linha ou ponto final
                for separator in ['\n\n', '\n', '. ', '! ', '? ']:
                    last_break = text.rfind(separator, start, end)
                    if last_break != -1:
                        end = last_break + len(separator)
                        break

            # Adicionar chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Mover para próximo chunk com sobreposição
            start = end - self.chunk_overlap if end < len(text) else end

        return chunks

    def get_document_stats(self, chunks: List[Dict]) -> Dict:
        """
        Retorna estatísticas sobre os chunks processados

        Args:
            chunks: Lista de chunks processados

        Returns:
            Dicionário com estatísticas
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_characters': 0,
                'avg_chunk_size': 0,
                'unique_sources': 0
            }

        total_chars = sum(len(chunk['text']) for chunk in chunks)
        sources = set(chunk['metadata']['source'] for chunk in chunks)

        return {
            'total_chunks': len(chunks),
            'total_characters': total_chars,
            'avg_chunk_size': total_chars // len(chunks),
            'unique_sources': len(sources),
            'sources': list(sources)
        }
