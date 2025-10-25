# Gerador de Relatórios de Performance SAP HANA

Sistema completo para coleta e geração de relatórios de performance do SAP HANA, incluindo métricas de sistema, usuários e tempos de resposta.

## Características

- **Métricas de Performance**:
  - Uso de CPU por host
  - Uso de memória (total e por serviço)
  - Uso de disco e armazenamento
  - Tempo de resposta de queries
  - Estatísticas de serviços HANA
  - Top tabelas por tamanho

- **Informações de Usuários**:
  - Total de usuários cadastrados (ativos e desativados)
  - Usuários atualmente logados
  - Resumo de conexões por usuário
  - Estatísticas de atividade
  - Usuários por role/privilégios

- **Formatos de Relatório**:
  - Excel (XLSX) com múltiplas abas
  - HTML com formatação profissional
  - Geração automática de resumo executivo

## Requisitos

- Python 3.7 ou superior
- SAP HANA Database
- Credenciais de acesso ao HANA com permissões de leitura nas views de sistema

## Instalação

1. Clone o repositório ou baixe os arquivos

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as credenciais de acesso:

Opção 1 - Usando arquivo .env:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

Opção 2 - Usando arquivo de configuração:
```bash
cp config/config.json.example config/config.json
# Edite o arquivo config.json com suas credenciais
```

## Configuração

### Arquivo .env

```env
HANA_HOST=seu-servidor-hana.com
HANA_PORT=30015
HANA_USER=seu_usuario
HANA_PASSWORD=sua_senha
HANA_DATABASE=SYSTEMDB
```

### Arquivo config.json

```json
{
  "hana": {
    "host": "seu-servidor-hana.com",
    "port": 30015,
    "user": "seu_usuario",
    "password": "sua_senha",
    "database": "SYSTEMDB"
  },
  "report": {
    "output_format": "excel",
    "output_dir": "reports",
    "include_charts": true,
    "retention_days": 30
  }
}
```

## Uso

### Uso Básico

Com credenciais no arquivo .env:
```bash
python main.py
```

### Uso com Parâmetros

```bash
python main.py --host servidor.com --port 30015 --user usuario --password senha
```

### Opções Disponíveis

```bash
python main.py --help
```

Parâmetros:
- `--host`: Endereço do servidor HANA
- `--port`: Porta de conexão (padrão: 30015)
- `--user`: Usuário do banco
- `--password`: Senha do usuário
- `--database`: Nome do banco de dados (padrão: SYSTEMDB)
- `--format`: Formato do relatório (excel, html, both - padrão: both)
- `--output-dir`: Diretório para salvar relatórios (padrão: reports)

### Exemplos

Gerar apenas relatório Excel:
```bash
python main.py --format excel
```

Gerar apenas relatório HTML:
```bash
python main.py --format html
```

Especificar diretório de saída:
```bash
python main.py --output-dir /caminho/para/relatorios
```

Conexão completa via linha de comando:
```bash
python main.py --host hana-server.empresa.com \
               --port 30015 \
               --user ADMIN \
               --password SenhaSegura123 \
               --database SYSTEMDB \
               --format both
```

## Estrutura do Projeto

```
hana_performance_reports/
├── main.py                 # Programa principal
├── requirements.txt        # Dependências Python
├── README.md              # Esta documentação
├── .env.example           # Exemplo de configuração de ambiente
├── hana_reports.log       # Log de execução (gerado automaticamente)
├── config/
│   └── config.json.example  # Exemplo de configuração JSON
├── src/
│   ├── hana_connection.py     # Gerenciamento de conexão HANA
│   ├── metrics_collector.py   # Coleta de métricas de performance
│   ├── user_collector.py      # Coleta de informações de usuários
│   └── report_generator.py    # Geração de relatórios
└── reports/                   # Diretório de relatórios gerados
    ├── hana_performance_report_YYYYMMDD_HHMMSS.xlsx
    └── hana_performance_report_YYYYMMDD_HHMMSS.html
```

## Métricas Coletadas

### Performance do Sistema
- **CPU**: Uso médio, máximo e mínimo por host
- **Memória**: Uso total, limite e percentual de utilização
- **Disco**: Espaço usado, total e percentual por volume
- **Tempo de Resposta**: Estatísticas de queries executadas
- **Serviços**: Status e consumo de recursos por serviço HANA
- **Tabelas**: Top tabelas por tamanho em memória

### Usuários e Conexões
- **Usuários Totais**: Contagem de todos os usuários do sistema
- **Usuários Ativos**: Usuários habilitados no sistema
- **Usuários Logados**: Lista de usuários com sessões ativas
- **Conexões**: Estatísticas de conexões por usuário e status
- **Atividade**: Queries executadas e tempo de execução por usuário
- **Roles**: Distribuição de usuários por perfil de acesso

## Formato dos Relatórios

### Relatório Excel

O relatório Excel contém as seguintes abas:
1. **Resumo**: Visão geral de todas as métricas
2. **CPU Usage**: Detalhes de uso de CPU
3. **Memory Usage**: Detalhes de uso de memória
4. **Disk Usage**: Detalhes de uso de disco
5. **Response Time**: Estatísticas de tempo de resposta
6. **Connections**: Informações de conexões ativas
7. **Services**: Status dos serviços HANA
8. **Top Tables**: Maiores tabelas do sistema
9. **Total Users**: Resumo de usuários totais
10. **Logged Users**: Usuários atualmente logados
11. **User Connections**: Resumo de conexões por usuário
12. **User Activity**: Atividade dos usuários
13. **Users by Role**: Distribuição por perfil

### Relatório HTML

O relatório HTML inclui:
- Design responsivo e profissional
- Resumo executivo com métricas principais
- Tabelas interativas com todos os dados
- Formatação com cores para melhor visualização

## Logs

O sistema gera logs automáticos no arquivo `hana_reports.log` com:
- Timestamp de cada operação
- Status de conexão
- Métricas coletadas
- Erros e avisos
- Arquivos gerados

## Segurança

**IMPORTANTE**:
- Nunca compartilhe o arquivo `.env` ou `config.json` com credenciais
- Adicione `.env` e `config.json` ao `.gitignore`
- Use usuários com permissões mínimas necessárias
- Considere usar variáveis de ambiente do sistema operacional

### Permissões Necessárias

O usuário HANA precisa ter acesso de leitura às seguintes views:
- `M_HOST_RESOURCE_UTILIZATION`
- `M_DISK_USAGE`
- `M_CONNECTIONS`
- `M_EXPENSIVE_STATEMENTS`
- `M_SERVICE_MEMORY`
- `M_CS_TABLES`
- `USERS`
- `GRANTED_PRIVILEGES`
- `GRANTED_ROLES`
- `M_PASSWORD_POLICY`

## Troubleshooting

### Erro de Conexão
```
Erro ao conectar ao HANA: [error message]
```
**Solução**: Verifique host, porta, usuário e senha. Confirme se o servidor HANA está acessível.

### Erro de Permissão
```
Erro ao executar query: insufficient privilege
```
**Solução**: O usuário precisa ter permissões de leitura nas views de sistema. Contate o administrador HANA.

### Timeout de Conexão
```
Connection timeout
```
**Solução**: Verifique firewall e conectividade de rede com o servidor HANA.

### Dependências Não Instaladas
```
ModuleNotFoundError: No module named 'hdbcli'
```
**Solução**: Execute `pip install -r requirements.txt`

## Agendamento Automático

### Linux/Unix (cron)

Para executar o relatório diariamente às 8h:
```bash
0 8 * * * cd /caminho/para/hana_performance_reports && python main.py
```

### Windows (Task Scheduler)

1. Abra o Agendador de Tarefas
2. Crie uma nova tarefa
3. Configure o gatilho (diário, semanal, etc.)
4. Configure a ação: `python C:\caminho\para\main.py`

## Personalização

Você pode personalizar o sistema editando os arquivos em `src/`:

- **metrics_collector.py**: Adicionar novas métricas de performance
- **user_collector.py**: Adicionar novas informações de usuários
- **report_generator.py**: Customizar formato e estilo dos relatórios

## Contribuindo

Sugestões e melhorias são bem-vindas! Para contribuir:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto é fornecido "como está", sem garantias de qualquer tipo.

## Suporte

Para problemas ou dúvidas:
1. Verifique a seção Troubleshooting
2. Consulte os logs em `hana_reports.log`
3. Abra uma issue no repositório

## Versão

**Versão**: 1.0.0
**Data**: 2025
**Compatibilidade**: SAP HANA 2.0+

## Changelog

### v1.0.0 (2025-10-25)
- Versão inicial
- Coleta de métricas de CPU, memória e disco
- Coleta de informações de usuários
- Geração de relatórios Excel e HTML
- Suporte a configuração via .env e linha de comando
