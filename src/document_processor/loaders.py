"""
Carregadores de diferentes tipos de documentos
"""

import os
from typing import List, Dict
from pathlib import Path
import pypdf
from docx import Document
import logging

logger = logging.getLogger(__name__)


class BaseLoader:
    """Classe base para carregadores de documentos"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    def load(self) -> Dict[str, any]:
        """Carrega o documento e retorna metadados e conteúdo"""
        raise NotImplementedError


class PDFLoader(BaseLoader):
    """Carregador de documentos PDF"""

    def load(self) -> Dict[str, any]:
        """Carrega um arquivo PDF e extrai texto e metadados"""
        logger.info(f"Carregando PDF: {self.file_path}")

        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)

                # Extrair metadados
                metadata = {
                    'source': str(self.file_path),
                    'filename': self.file_path.name,
                    'num_pages': len(pdf_reader.pages),
                    'type': 'pdf'
                }

                # Extrair texto de todas as páginas
                pages = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    pages.append({
                        'page_number': page_num + 1,
                        'text': text
                    })

                return {
                    'metadata': metadata,
                    'pages': pages
                }

        except Exception as e:
            logger.error(f"Erro ao carregar PDF {self.file_path}: {str(e)}")
            raise


class DOCXLoader(BaseLoader):
    """Carregador de documentos DOCX"""

    def load(self) -> Dict[str, any]:
        """Carrega um arquivo DOCX e extrai texto e metadados"""
        logger.info(f"Carregando DOCX: {self.file_path}")

        try:
            doc = Document(self.file_path)

            # Extrair metadados
            metadata = {
                'source': str(self.file_path),
                'filename': self.file_path.name,
                'type': 'docx'
            }

            # Extrair texto de todos os parágrafos
            paragraphs = []
            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    paragraphs.append({
                        'paragraph_number': i + 1,
                        'text': para.text
                    })

            return {
                'metadata': metadata,
                'paragraphs': paragraphs
            }

        except Exception as e:
            logger.error(f"Erro ao carregar DOCX {self.file_path}: {str(e)}")
            raise


class LoaderFactory:
    """Factory para criar loaders baseado no tipo de arquivo"""

    LOADERS = {
        '.pdf': PDFLoader,
        '.docx': DOCXLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str) -> BaseLoader:
        """Retorna o loader apropriado para o tipo de arquivo"""
        ext = Path(file_path).suffix.lower()

        if ext not in cls.LOADERS:
            raise ValueError(f"Tipo de arquivo não suportado: {ext}")

        return cls.LOADERS[ext](file_path)
