"""
Módulo de Relatórios de Performance SAP HANA

Este pacote fornece funcionalidades para coletar métricas de performance
do SAP HANA e gerar relatórios detalhados.
"""

__version__ = '1.0.0'
__author__ = 'Sistema de Relatórios HANA'

from .hana_connection import HanaConnection
from .metrics_collector import MetricsCollector
from .user_collector import UserCollector
from .report_generator import ReportGenerator

__all__ = [
    'HanaConnection',
    'MetricsCollector',
    'UserCollector',
    'ReportGenerator'
]
