"""
Módulo para coletar informações de usuários do SAP HANA
"""
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserCollector:
    """Classe para coletar informações de usuários do HANA"""

    def __init__(self, hana_connection):
        """
        Inicializa o coletor de informações de usuários

        Args:
            hana_connection: Instância de HanaConnection
        """
        self.conn = hana_connection

    def get_total_users(self):
        """Retorna o total de usuários cadastrados no sistema"""
        query = """
        SELECT
            COUNT(*) AS TOTAL_USERS,
            SUM(CASE WHEN USER_DEACTIVATED = 'TRUE' THEN 1 ELSE 0 END) AS DEACTIVATED_USERS,
            SUM(CASE WHEN USER_DEACTIVATED = 'FALSE' THEN 1 ELSE 0 END) AS ACTIVE_USERS
        FROM USERS
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Total de usuários coletado com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar total de usuários: {str(e)}")
            return pd.DataFrame()

    def get_logged_users(self):
        """Retorna informações sobre usuários atualmente logados"""
        query = """
        SELECT
            USER_NAME,
            CONNECTION_STATUS,
            CLIENT_HOST,
            CLIENT_IP,
            START_TIME,
            IDLE_TIME
        FROM M_CONNECTIONS
        WHERE CONNECTION_STATUS = 'RUNNING'
        ORDER BY START_TIME DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Usuários logados coletados com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar usuários logados: {str(e)}")
            return pd.DataFrame()

    def get_user_connections_summary(self):
        """Retorna resumo de conexões por usuário"""
        query = """
        SELECT
            USER_NAME,
            COUNT(*) AS TOTAL_CONNECTIONS,
            CONNECTION_STATUS,
            MIN(START_TIME) AS FIRST_CONNECTION,
            MAX(START_TIME) AS LAST_CONNECTION
        FROM M_CONNECTIONS
        GROUP BY USER_NAME, CONNECTION_STATUS
        ORDER BY TOTAL_CONNECTIONS DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Resumo de conexões por usuário coletado com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar resumo de conexões: {str(e)}")
            return pd.DataFrame()

    def get_user_privileges(self):
        """Retorna informações sobre privilégios de usuários"""
        query = """
        SELECT
            GRANTEE,
            GRANTEE_TYPE,
            PRIVILEGE,
            IS_GRANTABLE,
            COUNT(*) AS PRIVILEGE_COUNT
        FROM GRANTED_PRIVILEGES
        WHERE GRANTEE_TYPE = 'USER'
        GROUP BY GRANTEE, GRANTEE_TYPE, PRIVILEGE, IS_GRANTABLE
        ORDER BY GRANTEE, PRIVILEGE_COUNT DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Privilégios de usuários coletados com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar privilégios: {str(e)}")
            return pd.DataFrame()

    def get_user_activity_stats(self):
        """Retorna estatísticas de atividade dos usuários"""
        query = """
        SELECT
            USER_NAME,
            COUNT(*) AS STATEMENT_COUNT,
            ROUND(AVG(DURATION_MICROSEC) / 1000, 2) AS AVG_DURATION_MS,
            ROUND(SUM(DURATION_MICROSEC) / 1000000, 2) AS TOTAL_DURATION_SEC
        FROM M_EXPENSIVE_STATEMENTS
        WHERE START_TIME > ADD_SECONDS(CURRENT_TIMESTAMP, -3600)
        GROUP BY USER_NAME
        ORDER BY STATEMENT_COUNT DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Estatísticas de atividade coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas de atividade: {str(e)}")
            return pd.DataFrame()

    def get_failed_login_attempts(self):
        """Retorna tentativas de login falhadas"""
        query = """
        SELECT
            USER_NAME,
            COUNT(*) AS FAILED_ATTEMPTS,
            MAX(TIME) AS LAST_FAILED_ATTEMPT
        FROM M_PASSWORD_POLICY
        WHERE LAST_FAILED_CONNECT_TIMESTAMP IS NOT NULL
        GROUP BY USER_NAME
        ORDER BY FAILED_ATTEMPTS DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Tentativas de login falhadas coletadas com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar tentativas de login falhadas: {str(e)}")
            return pd.DataFrame()

    def get_users_by_role(self):
        """Retorna usuários agrupados por role"""
        query = """
        SELECT
            ROLE_NAME,
            COUNT(DISTINCT GRANTEE) AS USER_COUNT
        FROM GRANTED_ROLES
        WHERE GRANTEE_TYPE = 'USER'
        GROUP BY ROLE_NAME
        ORDER BY USER_COUNT DESC
        """
        try:
            results = self.conn.execute_query(query)
            columns = self.conn.get_column_names()
            df = pd.DataFrame(results, columns=columns)
            logger.info("Usuários por role coletados com sucesso")
            return df
        except Exception as e:
            logger.error(f"Erro ao coletar usuários por role: {str(e)}")
            return pd.DataFrame()

    def collect_all_user_info(self):
        """
        Coleta todas as informações de usuários

        Returns:
            Dicionário com todas as informações coletadas
        """
        logger.info("Iniciando coleta de informações de usuários...")

        user_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_users': self.get_total_users(),
            'logged_users': self.get_logged_users(),
            'connections_summary': self.get_user_connections_summary(),
            'user_activity': self.get_user_activity_stats(),
            'users_by_role': self.get_users_by_role()
        }

        logger.info("Coleta de informações de usuários concluída!")
        return user_info
