"""
Módulo para gerar relatórios de performance do SAP HANA
"""
import pandas as pd
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Classe para gerar relatórios consolidados"""

    def __init__(self, output_dir='reports'):
        """
        Inicializa o gerador de relatórios

        Args:
            output_dir: Diretório onde os relatórios serão salvos
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_excel_report(self, metrics, user_info, filename=None):
        """
        Gera relatório em formato Excel

        Args:
            metrics: Dicionário com métricas coletadas
            user_info: Dicionário com informações de usuários
            filename: Nome do arquivo (opcional)

        Returns:
            Caminho do arquivo gerado
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'hana_performance_report_{timestamp}.xlsx'

        filepath = os.path.join(self.output_dir, filename)

        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Página de Resumo
                self._create_summary_sheet(writer, metrics, user_info)

                # Métricas de Performance
                if not metrics['cpu_usage'].empty:
                    metrics['cpu_usage'].to_excel(writer, sheet_name='CPU Usage', index=False)

                if not metrics['memory_usage'].empty:
                    metrics['memory_usage'].to_excel(writer, sheet_name='Memory Usage', index=False)

                if not metrics['disk_usage'].empty:
                    metrics['disk_usage'].to_excel(writer, sheet_name='Disk Usage', index=False)

                if not metrics['response_time'].empty:
                    metrics['response_time'].to_excel(writer, sheet_name='Response Time', index=False)

                if not metrics['connections'].empty:
                    metrics['connections'].to_excel(writer, sheet_name='Connections', index=False)

                if not metrics['services'].empty:
                    metrics['services'].to_excel(writer, sheet_name='Services', index=False)

                if not metrics['top_tables'].empty:
                    metrics['top_tables'].to_excel(writer, sheet_name='Top Tables', index=False)

                # Informações de Usuários
                if not user_info['total_users'].empty:
                    user_info['total_users'].to_excel(writer, sheet_name='Total Users', index=False)

                if not user_info['logged_users'].empty:
                    user_info['logged_users'].to_excel(writer, sheet_name='Logged Users', index=False)

                if not user_info['connections_summary'].empty:
                    user_info['connections_summary'].to_excel(writer, sheet_name='User Connections', index=False)

                if not user_info['user_activity'].empty:
                    user_info['user_activity'].to_excel(writer, sheet_name='User Activity', index=False)

                if not user_info['users_by_role'].empty:
                    user_info['users_by_role'].to_excel(writer, sheet_name='Users by Role', index=False)

            logger.info(f"Relatório Excel gerado com sucesso: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Erro ao gerar relatório Excel: {str(e)}")
            return None

    def _create_summary_sheet(self, writer, metrics, user_info):
        """Cria a página de resumo do relatório"""
        summary_data = []

        # Informações Gerais
        summary_data.append(['RELATÓRIO DE PERFORMANCE SAP HANA', ''])
        summary_data.append(['Data de Geração', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        summary_data.append(['', ''])

        # Resumo de Usuários
        summary_data.append(['=== USUÁRIOS ===', ''])
        if not user_info['total_users'].empty:
            total_users = user_info['total_users'].iloc[0]
            summary_data.append(['Total de Usuários', total_users['TOTAL_USERS']])
            summary_data.append(['Usuários Ativos', total_users['ACTIVE_USERS']])
            summary_data.append(['Usuários Desativados', total_users['DEACTIVATED_USERS']])

        if not user_info['logged_users'].empty:
            logged_count = len(user_info['logged_users'])
            summary_data.append(['Usuários Logados Atualmente', logged_count])

        summary_data.append(['', ''])

        # Resumo de Performance
        summary_data.append(['=== PERFORMANCE ===', ''])

        if not metrics['cpu_usage'].empty:
            avg_cpu = metrics['cpu_usage']['AVG_CPU_USAGE'].mean()
            summary_data.append(['CPU Média (%)', f'{avg_cpu:.2f}'])

        if not metrics['memory_usage'].empty:
            total_memory_used = metrics['memory_usage']['MEMORY_USED_GB'].sum()
            summary_data.append(['Memória Total em Uso (GB)', f'{total_memory_used:.2f}'])

        if not metrics['response_time'].empty:
            avg_response = metrics['response_time']['AVG_RESPONSE_TIME_MS'].mean()
            summary_data.append(['Tempo de Resposta Médio (ms)', f'{avg_response:.2f}'])

        if not metrics['connections'].empty:
            total_conn = metrics['connections']['TOTAL_CONNECTIONS'].sum()
            summary_data.append(['Total de Conexões', total_conn])

        summary_data.append(['', ''])

        # Resumo de Armazenamento
        summary_data.append(['=== ARMAZENAMENTO ===', ''])
        if not metrics['disk_usage'].empty:
            total_disk_used = metrics['disk_usage']['USED_GB'].sum()
            total_disk = metrics['disk_usage']['TOTAL_GB'].sum()
            summary_data.append(['Disco Usado (GB)', f'{total_disk_used:.2f}'])
            summary_data.append(['Disco Total (GB)', f'{total_disk:.2f}'])
            if total_disk > 0:
                disk_pct = (total_disk_used / total_disk) * 100
                summary_data.append(['Uso de Disco (%)', f'{disk_pct:.2f}'])

        # Criar DataFrame e salvar
        summary_df = pd.DataFrame(summary_data, columns=['Métrica', 'Valor'])
        summary_df.to_excel(writer, sheet_name='Resumo', index=False)

    def generate_html_report(self, metrics, user_info, filename=None):
        """
        Gera relatório em formato HTML

        Args:
            metrics: Dicionário com métricas coletadas
            user_info: Dicionário com informações de usuários
            filename: Nome do arquivo (opcional)

        Returns:
            Caminho do arquivo gerado
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'hana_performance_report_{timestamp}.html'

        filepath = os.path.join(self.output_dir, filename)

        try:
            html_content = self._generate_html_content(metrics, user_info)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Relatório HTML gerado com sucesso: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Erro ao gerar relatório HTML: {str(e)}")
            return None

    def _generate_html_content(self, metrics, user_info):
        """Gera o conteúdo HTML do relatório"""
        html = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Performance SAP HANA</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #0070d2;
                    border-bottom: 3px solid #0070d2;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #333;
                    margin-top: 30px;
                    border-bottom: 2px solid #ddd;
                    padding-bottom: 5px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                th {
                    background-color: #0070d2;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }
                td {
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }
                tr:hover {
                    background-color: #f0f0f0;
                }
                .summary-box {
                    background-color: #e8f4f8;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                    border-left: 4px solid #0070d2;
                }
                .metric {
                    display: inline-block;
                    margin: 10px 20px 10px 0;
                }
                .metric-label {
                    font-weight: bold;
                    color: #666;
                }
                .metric-value {
                    font-size: 1.2em;
                    color: #0070d2;
                }
                .timestamp {
                    color: #666;
                    font-style: italic;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Relatório de Performance SAP HANA</h1>
                <p class="timestamp">Gerado em: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>

                <div class="summary-box">
                    <h2>Resumo Executivo</h2>
        """

        # Adicionar resumo de usuários
        if not user_info['total_users'].empty:
            total_users = user_info['total_users'].iloc[0]
            html += f"""
                    <div class="metric">
                        <span class="metric-label">Total de Usuários:</span>
                        <span class="metric-value">{total_users['TOTAL_USERS']}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Usuários Ativos:</span>
                        <span class="metric-value">{total_users['ACTIVE_USERS']}</span>
                    </div>
            """

        if not user_info['logged_users'].empty:
            logged_count = len(user_info['logged_users'])
            html += f"""
                    <div class="metric">
                        <span class="metric-label">Usuários Logados:</span>
                        <span class="metric-value">{logged_count}</span>
                    </div>
            """

        # Adicionar métricas de performance
        if not metrics['cpu_usage'].empty:
            avg_cpu = metrics['cpu_usage']['AVG_CPU_USAGE'].mean()
            html += f"""
                    <div class="metric">
                        <span class="metric-label">CPU Média:</span>
                        <span class="metric-value">{avg_cpu:.2f}%</span>
                    </div>
            """

        if not metrics['response_time'].empty:
            avg_response = metrics['response_time']['AVG_RESPONSE_TIME_MS'].mean()
            html += f"""
                    <div class="metric">
                        <span class="metric-label">Tempo de Resposta Médio:</span>
                        <span class="metric-value">{avg_response:.2f} ms</span>
                    </div>
            """

        html += """
                </div>
        """

        # Adicionar tabelas de dados
        sections = [
            ('CPU Usage', metrics.get('cpu_usage')),
            ('Memory Usage', metrics.get('memory_usage')),
            ('Disk Usage', metrics.get('disk_usage')),
            ('Response Time', metrics.get('response_time')),
            ('Active Connections', metrics.get('connections')),
            ('Logged Users', user_info.get('logged_users')),
            ('User Activity', user_info.get('user_activity'))
        ]

        for title, df in sections:
            if df is not None and not df.empty:
                html += f"<h2>{title}</h2>"
                html += df.to_html(index=False, classes='data-table')

        html += """
            </div>
        </body>
        </html>
        """

        return html
