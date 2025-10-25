# SAPDEMO - Relatório de Performance SAP HANA

Sistema completo para geração de relatórios de performance do SAP HANA utilizando AMDP (ABAP Managed Database Procedures).

## 📋 Visão Geral

Este projeto fornece ferramentas para monitoramento e análise de performance do SAP HANA, incluindo:

- **Informações de Usuários**: Total de usuários, usuários logados, bloqueados e detalhamento de sessões
- **Tempo de Resposta**: Análise de performance de queries, tempos médio/mínimo/máximo
- **Uso de Memória**: Monitoramento de memória total, utilizada e livre por serviço
- **Conexões Ativas**: Análise de conexões ativas, inativas e detalhamento por aplicação

## 🚀 Componentes

### Programas ABAP

1. **ZHANA_PERFORMANCE_REPORT** (`src/zhana_performance_report.prog.abap`)
   - Programa principal para geração de relatórios
   - Interface de seleção amigável
   - Múltiplas opções de relatório

2. **ZHANA_PERF_CL** (`src/zhana_perf_cl.clas.abap`)
   - Classe AMDP para desenvolvimento/testes
   - Queries simuladas para demonstração

3. **ZHANA_PERF_CL (Produção)** (`src/zhana_perf_cl_production.clas.abap`)
   - Classe AMDP com queries reais
   - Usa views de sistema do HANA
   - Pronto para ambiente produtivo

## 📚 Documentação

- **[Documentação Completa](docs/HANA_PERFORMANCE_REPORT_DOC.md)**: Guia completo de instalação e uso
- **[Referência de Queries](docs/HANA_QUERIES_REFERENCE.md)**: Queries úteis do HANA

## 🔧 Instalação

### Pré-requisitos

- SAP NetWeaver 7.4 ou superior
- SAP HANA Database
- Autorização para executar AMDP
- Acesso às views de sistema do HANA

### Passos

1. **Criar a Classe AMDP:**
   ```
   Transação: SE24
   Nome: ZHANA_PERF_CL
   Tipo: Classe ABAP
   ```
   - Copiar conteúdo de `src/zhana_perf_cl.clas.abap` (desenvolvimento)
   - OU `src/zhana_perf_cl_production.clas.abap` (produção)
   - Ativar a classe

2. **Criar o Programa:**
   ```
   Transação: SE38
   Nome: ZHANA_PERFORMANCE_REPORT
   Tipo: Programa Executável
   ```
   - Copiar conteúdo de `src/zhana_performance_report.prog.abap`
   - Ativar o programa

3. **Executar:**
   ```
   Transação: SA38
   Programa: ZHANA_PERFORMANCE_REPORT
   ```

## 💡 Uso Rápido

### Executar Relatório Completo

1. Execute a transação **SA38**
2. Digite: **ZHANA_PERFORMANCE_REPORT**
3. Marque todas as opções:
   - ✓ Informações de usuários
   - ✓ Tempo de resposta
   - ✓ Uso de memória
   - ✓ Conexões ativas
   - ✓ Detalhamento completo
4. Execute (F8)

### Parâmetros

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| P_USERS | Exibir info de usuários | ✓ |
| P_RESP | Exibir tempo de resposta | ✓ |
| P_MEM | Exibir uso de memória | ✓ |
| P_CONN | Exibir conexões | ✓ |
| P_DETL | Detalhamento completo | ✗ |
| P_DAYS | Dias para análise | 1 |

## 📊 Exemplo de Saída

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
```

## 🔐 Autorizações Necessárias

| Objeto | Descrição |
|--------|-----------|
| S_DEVELOP | Desenvolvimento ABAP |
| S_TABU_NAM | Acesso a USR02, USR41 |
| S_DATASET | Leitura de dados |

## 🛠️ Tecnologias

- **ABAP**: Linguagem principal
- **AMDP**: ABAP Managed Database Procedures
- **SQLScript**: Linguagem nativa do HANA
- **SAP HANA**: Banco de dados in-memory

## 📈 Features

- ✅ Relatórios de performance em tempo real
- ✅ Análise de usuários e sessões
- ✅ Monitoramento de memória
- ✅ Análise de tempo de resposta
- ✅ Detalhamento de conexões
- ✅ Alertas de uso crítico
- ✅ Interface amigável
- ✅ Exportável e customizável

## 🔜 Melhorias Futuras

- [ ] Exportação para Excel/PDF
- [ ] Envio automático por e-mail
- [ ] Dashboard Web (Fiori/UI5)
- [ ] Análise histórica com gráficos
- [ ] Integração com Solution Manager
- [ ] Alertas automáticos configuráveis
- [ ] API REST para integração

## 📖 Estrutura do Projeto

```
SAPDEMO/
├── src/
│   ├── zhana_performance_report.prog.abap    # Programa principal
│   ├── zhana_perf_cl.clas.abap              # Classe AMDP (dev)
│   └── zhana_perf_cl_production.clas.abap   # Classe AMDP (prod)
├── docs/
│   ├── HANA_PERFORMANCE_REPORT_DOC.md       # Documentação completa
│   └── HANA_QUERIES_REFERENCE.md            # Referência de queries
└── README.md                                 # Este arquivo
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é fornecido como exemplo educacional e pode ser adaptado conforme necessário.

## 👥 Autores

Desenvolvido para demonstração de capacidades AMDP e monitoramento SAP HANA.

## 🆘 Suporte

Para questões, melhorias ou bugs:
- Criar issue no repositório
- Contatar a equipe de Basis/HANA

## 🌟 Agradecimentos

- Comunidade SAP
- Documentação oficial SAP HANA
- Contribuidores do projeto

---

**Versão:** 1.0
**Data:** Outubro 2025
**Desenvolvido com:** AMDP (ABAP Managed Database Procedures)
