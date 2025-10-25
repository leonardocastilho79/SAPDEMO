# Relatório de Performance do SAP HANA

## Visão Geral

Este projeto fornece um programa ABAP completo para gerar relatórios detalhados de performance do SAP HANA, utilizando AMDP (ABAP Managed Database Procedures) para executar consultas nativas diretamente no banco de dados HANA.

## Componentes

### 1. ZHANA_PERFORMANCE_REPORT (Program)
Programa principal que gera o relatório de performance com interface de seleção amigável.

### 2. ZHANA_PERF_CL (Class)
Classe AMDP que contém métodos para executar consultas nativas SQLScript no HANA.

## Funcionalidades

### 📊 Informações de Usuários
- Total de usuários cadastrados no sistema
- Usuários atualmente logados
- Usuários bloqueados
- Percentual de uso
- Detalhamento de sessões ativas

### ⏱️ Tempo de Resposta
- Tempo médio de resposta das queries
- Tempo mínimo e máximo
- Top 10 queries mais lentas
- Análise de performance por período

### 💾 Uso de Memória
- Memória total alocada
- Memória utilizada e livre
- Percentual de uso
- Detalhamento por serviço (Index Server, Name Server, XS Engine)
- Alertas de uso crítico (>80% e >90%)

### 🔗 Conexões Ativas
- Total de conexões
- Conexões ativas e inativas
- Detalhamento por host, porta e usuário
- Aplicações conectadas

## Como Usar

### Instalação

1. **Criar a classe AMDP:**
   - Transação: SE24
   - Nome: ZHANA_PERF_CL
   - Copiar conteúdo do arquivo `src/zhana_perf_cl.clas.abap`
   - Ativar a classe

2. **Criar o programa:**
   - Transação: SE38
   - Nome: ZHANA_PERFORMANCE_REPORT
   - Copiar conteúdo do arquivo `src/zhana_performance_report.prog.abap`
   - Ativar o programa

### Execução

1. Execute a transação **SE38** ou **SA38**
2. Digite o programa: **ZHANA_PERFORMANCE_REPORT**
3. Configure os parâmetros de seleção:

   **Opções de Relatório:**
   - ☑ Informações de usuários
   - ☑ Tempo de resposta
   - ☑ Uso de memória
   - ☑ Conexões ativas
   - ☐ Detalhamento completo

   **Período de Análise:**
   - Dias para análise: 1 (padrão)

4. Execute (F8)

## Parâmetros de Seleção

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| P_USERS | Exibir informações de usuários | ✓ |
| P_RESP | Exibir tempo de resposta | ✓ |
| P_MEM | Exibir uso de memória | ✓ |
| P_CONN | Exibir conexões ativas | ✓ |
| P_DETL | Exibir detalhamento completo | ✗ |
| P_DAYS | Número de dias para análise | 1 |

## Estrutura Técnica

### Tipos de Dados (Types)

```abap
TY_USER_INFO         - Informações de usuários
TY_RESPONSE_TIME     - Tempos de resposta
TY_MEMORY_USAGE      - Uso de memória
TY_CONNECTION_INFO   - Informações de conexão
```

### Métodos AMDP

1. **GET_USER_STATISTICS**
   - Retorna estatísticas de usuários do sistema
   - Consulta tabelas: USR02, USR41

2. **GET_RESPONSE_TIMES**
   - Analisa tempos de resposta das queries
   - Parâmetro: iv_days (período de análise)

3. **GET_MEMORY_STATISTICS**
   - Coleta uso de memória por serviço
   - Retorna total, usado e livre

4. **GET_CONNECTION_STATISTICS**
   - Lista conexões ativas e inativas
   - Detalhamento por host e usuário

## Views de Sistema HANA (Para Produção)

Para ambiente de produção, substitua as queries simuladas pelas views reais do HANA:

### Memória
```sql
SELECT * FROM M_HOST_RESOURCE_UTILIZATION
SELECT * FROM M_SERVICE_MEMORY
SELECT * FROM M_MEMORY_OBJECTS
```

### Conexões
```sql
SELECT * FROM M_CONNECTIONS
SELECT * FROM M_SERVICE_THREADS
```

### Performance
```sql
SELECT * FROM M_SQL_PLAN_CACHE
SELECT * FROM M_EXPENSIVE_STATEMENTS
SELECT * FROM M_LOAD_HISTORY_SERVICE
```

### Usuários e Sessões
```sql
SELECT * FROM M_SESSION_CONTEXT
SELECT * FROM M_ACTIVE_STATEMENTS
```

## Exemplo de Saída

```
═══════════════════════════════════════════════════════════════════════
          RELATÓRIO DE PERFORMANCE DO SAP HANA
═══════════════════════════════════════════════════════════════════════
Data: 25.10.2025   Hora: 14:30:00
Sistema: S4D   Mandante: 100
─────────────────────────────────────────────────────────────────────

📊 INFORMAÇÕES DE USUÁRIOS
─────────────────────────────────────────────────────────────────────
Total de Usuários Cadastrados: 150
Usuários Atualmente Logados:   45
Usuários Bloqueados:            5
Percentual de Uso:              30.00%

⏱️ TEMPO DE RESPOSTA DO SISTEMA
─────────────────────────────────────────────────────────────────────
Tempo Médio de Resposta: 245.320 ms
Tempo Mínimo:            12.450 ms
Tempo Máximo:            4850.120 ms

💾 USO DE MEMÓRIA DO HANA
─────────────────────────────────────────────────────────────────────
Memória Total Alocada:  2048 GB
Memória Utilizada:      1536 GB
Memória Livre:          512 GB
Percentual de Uso:      75.00%

🔗 CONEXÕES ATIVAS
─────────────────────────────────────────────────────────────────────
Total de Conexões:      50
Conexões Ativas:        35
Conexões Inativas:      15

═══════════════════════════════════════════════════════════════════════
                    FIM DO RELATÓRIO
═══════════════════════════════════════════════════════════════════════
```

## Melhorias Futuras

1. **Exportação de Dados**
   - Exportar para Excel (OLE)
   - Exportar para PDF
   - Envio automático por e-mail

2. **Alertas Automáticos**
   - Configuração de thresholds
   - Notificações quando limites são atingidos

3. **Análise Histórica**
   - Salvar dados em tabelas Z
   - Gráficos de tendência
   - Comparação temporal

4. **Dashboard Web**
   - Interface Fiori/UI5
   - Atualização em tempo real
   - Visualizações gráficas

5. **Integração com Monitoring**
   - CCMS (Computing Center Management System)
   - Solution Manager
   - DBA Cockpit

## Requisitos de Sistema

- SAP NetWeaver 7.4 ou superior
- SAP HANA Database
- Autorização para executar AMDP
- Acesso às views de sistema do HANA

## Autorizações Necessárias

| Objeto de Autorização | Descrição |
|------------------------|-----------|
| S_DEVELOP | Desenvolvimento ABAP |
| S_TABU_NAM | Acesso tabelas USR02, USR41 |
| S_DATASET | Leitura de dados |

## Troubleshooting

### Erro: "AMDP Execution Failed"
**Solução:** Verificar se o usuário tem permissões no HANA para acessar as views de sistema.

### Erro: "Class ZHANA_PERF_CL not found"
**Solução:** Ativar a classe AMDP antes de executar o programa.

### Performance lenta
**Solução:**
- Reduzir o período de análise (parâmetro P_DAYS)
- Desabilitar "Detalhamento completo"
- Otimizar queries AMDP

## Suporte e Contribuições

Para questões, melhorias ou bugs:
- Criar issue no repositório
- Contatar a equipe de Basis/HANA

## Licença

Este código é fornecido como exemplo educacional e pode ser adaptado conforme necessário.

---

**Desenvolvido com AMDP (ABAP Managed Database Procedures)**
**Versão: 1.0**
**Data: Outubro 2025**
