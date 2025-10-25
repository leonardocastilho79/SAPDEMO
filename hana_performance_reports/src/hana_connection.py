"""
Módulo para gerenciar conexões com SAP HANA
"""
import os
from hdbcli import dbapi
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HanaConnection:
    """Classe para gerenciar a conexão com SAP HANA"""

    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        """
        Inicializa a conexão com SAP HANA

        Args:
            host: Endereço do servidor HANA
            port: Porta de conexão
            user: Usuário do banco
            password: Senha do usuário
            database: Nome do banco de dados
        """
        load_dotenv()

        self.host = host or os.getenv('HANA_HOST')
        self.port = port or os.getenv('HANA_PORT', 30015)
        self.user = user or os.getenv('HANA_USER')
        self.password = password or os.getenv('HANA_PASSWORD')
        self.database = database or os.getenv('HANA_DATABASE', 'SYSTEMDB')

        self.connection = None
        self.cursor = None

    def connect(self):
        """Estabelece conexão com o banco HANA"""
        try:
            logger.info(f"Conectando ao SAP HANA em {self.host}:{self.port}")
            self.connection = dbapi.connect(
                address=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                databaseName=self.database
            )
            self.cursor = self.connection.cursor()
            logger.info("Conexão estabelecida com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao HANA: {str(e)}")
            return False

    def disconnect(self):
        """Fecha a conexão com o banco"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Conexão fechada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão: {str(e)}")

    def execute_query(self, query, params=None):
        """
        Executa uma query no banco HANA

        Args:
            query: SQL query a ser executada
            params: Parâmetros da query (opcional)

        Returns:
            Lista de resultados
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            return None

    def get_column_names(self):
        """Retorna os nomes das colunas da última query executada"""
        if self.cursor and self.cursor.description:
            return [desc[0] for desc in self.cursor.description]
        return []

    def __enter__(self):
        """Suporte para uso com 'with' statement"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha a conexão ao sair do contexto 'with'"""
        self.disconnect()
