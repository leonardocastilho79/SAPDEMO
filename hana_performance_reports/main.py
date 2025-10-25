#!/usr/bin/env python3
"""
Programa Principal - Gerador de Relatórios de Performance SAP HANA

Este programa coleta métricas de performance do SAP HANA e gera relatórios
detalhados sobre:
- Performance do sistema (CPU, memória, disco)
- Usuários totais e logados
- Tempos de resposta
- Conexões ativas
- Estatísticas de serviços

Autor: Sistema de Relatórios HANA
Data: 2025
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hana_connection import HanaConnection
from metrics_collector import MetricsCollector
from user_collector import UserCollector
from report_generator import ReportGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hana_reports.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Gerador de Relatórios de Performance SAP HANA'
    )

    parser.add_argument(
        '--host',
        help='Endereço do servidor HANA'
    )

    parser.add_argument(
        '--port',
        type=int,
        help='Porta de conexão HANA'
    )

    parser.add_argument(
        '--user',
        help='Usuário do banco'
    )

    parser.add_argument(
        '--password',
        help='Senha do usuário'
    )

    parser.add_argument(
        '--database',
        help='Nome do banco de dados'
    )

    parser.add_argument(
        '--format',
        choices=['excel', 'html', 'both'],
        default='both',
        help='Formato do relatório (padrão: both)'
    )

    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Diretório para salvar os relatórios (padrão: reports)'
    )

    return parser.parse_args()


def print_banner():
    """Imprime o banner do programa"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     Gerador de Relatórios de Performance SAP HANA        ║
    ║                                                           ║
    ║     Coleta e analisa métricas de performance do HANA     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Função principal do programa"""
    print_banner()

    # Parse argumentos
    args = parse_arguments()

    logger.info("=" * 60)
    logger.info("Iniciando geração de relatórios SAP HANA")
    logger.info("=" * 60)

    try:
        # Conectar ao HANA
        logger.info("Estabelecendo conexão com SAP HANA...")
        with HanaConnection(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database
        ) as conn:

            if not conn.connection:
                logger.error("Falha ao conectar ao SAP HANA. Verifique as credenciais.")
                return 1

            # Coletar métricas de performance
            logger.info("Coletando métricas de performance...")
            metrics_collector = MetricsCollector(conn)
            metrics = metrics_collector.collect_all_metrics()

            # Coletar informações de usuários
            logger.info("Coletando informações de usuários...")
            user_collector = UserCollector(conn)
            user_info = user_collector.collect_all_user_info()

            # Gerar relatórios
            logger.info("Gerando relatórios...")
            report_gen = ReportGenerator(output_dir=args.output_dir)

            generated_files = []

            if args.format in ['excel', 'both']:
                excel_file = report_gen.generate_excel_report(metrics, user_info)
                if excel_file:
                    generated_files.append(excel_file)
                    logger.info(f"✓ Relatório Excel gerado: {excel_file}")

            if args.format in ['html', 'both']:
                html_file = report_gen.generate_html_report(metrics, user_info)
                if html_file:
                    generated_files.append(html_file)
                    logger.info(f"✓ Relatório HTML gerado: {html_file}")

            # Resumo final
            logger.info("=" * 60)
            logger.info("RESUMO DA EXECUÇÃO")
            logger.info("=" * 60)

            # Estatísticas de usuários
            if not user_info['total_users'].empty:
                total_users = user_info['total_users'].iloc[0]
                logger.info(f"Total de Usuários: {total_users['TOTAL_USERS']}")
                logger.info(f"Usuários Ativos: {total_users['ACTIVE_USERS']}")
                logger.info(f"Usuários Desativados: {total_users['DEACTIVATED_USERS']}")

            if not user_info['logged_users'].empty:
                logged_count = len(user_info['logged_users'])
                logger.info(f"Usuários Logados Atualmente: {logged_count}")

            # Estatísticas de performance
            if not metrics['cpu_usage'].empty:
                avg_cpu = metrics['cpu_usage']['AVG_CPU_USAGE'].mean()
                logger.info(f"CPU Média: {avg_cpu:.2f}%")

            if not metrics['memory_usage'].empty:
                total_memory = metrics['memory_usage']['MEMORY_USED_GB'].sum()
                logger.info(f"Memória Total em Uso: {total_memory:.2f} GB")

            if not metrics['response_time'].empty:
                avg_response = metrics['response_time']['AVG_RESPONSE_TIME_MS'].mean()
                logger.info(f"Tempo de Resposta Médio: {avg_response:.2f} ms")

            logger.info("=" * 60)
            logger.info(f"Relatórios gerados com sucesso!")
            logger.info(f"Total de arquivos gerados: {len(generated_files)}")
            for file in generated_files:
                logger.info(f"  - {file}")
            logger.info("=" * 60)

            return 0

    except KeyboardInterrupt:
        logger.warning("\nExecução interrompida pelo usuário")
        return 130

    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
