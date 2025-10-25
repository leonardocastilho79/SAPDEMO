"""
Módulo para coletar métricas de performance do SAP HANA
"""
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Classe para coletar métricas de performance do HANA"""

    def __init__(self, hana_connection):
        """
        Inicializa o coletor de métricas

        Args:
            hana_connection: Instância de HanaConnection
        """
        self.conn = hana_connection

    def get_cpu_usage(self):
        """Coleta métricas de uso de CPU"""
        query = """
        SELECT
            HOST,
            ROUND(AVG(CPU), 2) AS AVG_CPU_USAGE,
            ROUND(MAX(CPU), 2) AS MAX_CPU_USAGE,
            ROUND(MIN(CPU), 2) AS MIN_CPU_USAGE
        FROM M_HOST_RESOURCE_UTILIZATION
        GROUP BY HOST
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Métricas de CPU coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de CPU: {str(e)}")
            return pd.DataFrame()

    def get_memory_usage(self):
        """Coleta métricas de uso de memória"""
        query = """
        SELECT
            HOST,
            ROUND(TOTAL_MEMORY_USED_SIZE / 1024 / 1024 / 1024, 2) AS MEMORY_USED_GB,
            ROUND(ALLOCATION_LIMIT / 1024 / 1024 / 1024, 2) AS MEMORY_LIMIT_GB,
            ROUND((TOTAL_MEMORY_USED_SIZE / ALLOCATION_LIMIT * 100), 2) AS MEMORY_USAGE_PCT
        FROM M_HOST_RESOURCE_UTILIZATION
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Métricas de memória coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de memória: {str(e)}")
            return pd.DataFrame()

    def get_disk_usage(self):
        """Coleta métricas de uso de disco"""
        query = """
        SELECT
            HOST,
            PATH,
            ROUND(USED_SIZE / 1024 / 1024 / 1024, 2) AS USED_GB,
            ROUND(TOTAL_SIZE / 1024 / 1024 / 1024, 2) AS TOTAL_GB,
            ROUND((USED_SIZE / TOTAL_SIZE * 100), 2) AS USAGE_PCT
        FROM M_DISK_USAGE
        WHERE USAGE_TYPE = 'DATA'
        ORDER BY HOST, USAGE_PCT DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Métricas de disco coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de disco: {str(e)}")
            return pd.DataFrame()

    def get_active_connections(self):
        """Coleta informações sobre conexões ativas"""
        query = """
        SELECT
            COUNT(*) AS TOTAL_CONNECTIONS,
            CONNECTION_STATUS,
            COUNT(DISTINCT USER_NAME) AS UNIQUE_USERS
        FROM M_CONNECTIONS
        GROUP BY CONNECTION_STATUS
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Métricas de conexões coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de conexões: {str(e)}")
            return pd.DataFrame()

    def get_response_time_stats(self):
        """Coleta estatísticas de tempo de resposta"""
        query = """
        SELECT
            HOST,
            ROUND(AVG(DURATION_MICROSEC) / 1000, 2) AS AVG_RESPONSE_TIME_MS,
            ROUND(MAX(DURATION_MICROSEC) / 1000, 2) AS MAX_RESPONSE_TIME_MS,
            ROUND(MIN(DURATION_MICROSEC) / 1000, 2) AS MIN_RESPONSE_TIME_MS,
            COUNT(*) AS TOTAL_STATEMENTS
        FROM M_EXPENSIVE_STATEMENTS
        WHERE START_TIME > ADD_SECONDS(CURRENT_TIMESTAMP, -3600)
        GROUP BY HOST
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Métricas de tempo de resposta coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de tempo de resposta: {str(e)}")
            return pd.DataFrame()

    def get_service_statistics(self):
        """Coleta estatísticas dos serviços HANA"""
        query = """
        SELECT
            HOST,
            SERVICE_NAME,
            ACTIVE_STATUS,
            ROUND(TOTAL_MEMORY_USED_SIZE / 1024 / 1024, 2) AS MEMORY_USED_MB,
            PROCESS_CPU
        FROM M_SERVICE_MEMORY
        ORDER BY MEMORY_USED_MB DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Estatísticas de serviços coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas de serviços: {str(e)}")
            return pd.DataFrame()

    def get_table_sizes(self, top_n=20):
        """
        Coleta tamanhos das maiores tabelas

        Args:
            top_n: Número de maiores tabelas a retornar
        """
        query = f"""
        SELECT TOP {top_n}
            SCHEMA_NAME,
            TABLE_NAME,
            ROUND(MEMORY_SIZE_IN_TOTAL / 1024 / 1024, 2) AS SIZE_MB,
            RECORD_COUNT
        FROM M_CS_TABLES
        ORDER BY MEMORY_SIZE_IN_TOTAL DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info(f"Top {top_n} tabelas coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar tamanhos de tabelas: {str(e)}")
            return pd.DataFrame()

    def collect_all_metrics(self):
        """
        Coleta todas as métricas disponíveis

        Returns:
            Dicionário com todas as métricas coletadas
        """
        logger.info("Iniciando coleta de todas as métricas...")

        metrics = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu_usage': self.get_cpu_usage(),
            'memory_usage': self.get_memory_usage(),
            'disk_usage': self.get_disk_usage(),
            'connections': self.get_active_connections(),
            'response_time': self.get_response_time_stats(),
            'services': self.get_service_statistics(),
            'top_tables': self.get_table_sizes()
        }

        logger.info("Coleta de métricas concluída!")
        return metrics
