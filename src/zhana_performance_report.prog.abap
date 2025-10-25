*&---------------------------------------------------------------------*
*& Report ZHANA_PERFORMANCE_REPORT
*&---------------------------------------------------------------------*
*& Programa para gerar relatórios de performance do SAP HANA
*& Desenvolvido com AMDP (ABAP Managed Database Procedures)
*&---------------------------------------------------------------------*
REPORT zhana_performance_report.

*----------------------------------------------------------------------*
* Declarações de Dados
*----------------------------------------------------------------------*
DATA: lt_users         TYPE TABLE OF zhana_perf_cl=>ty_user_info,
      lt_response_time TYPE TABLE OF zhana_perf_cl=>ty_response_time,
      lt_memory_usage  TYPE TABLE OF zhana_perf_cl=>ty_memory_usage,
      lt_connections   TYPE TABLE OF zhana_perf_cl=>ty_connection_info,
      lv_total_users   TYPE i,
      lv_logged_users  TYPE i,
      lv_timestamp     TYPE timestamp.

*----------------------------------------------------------------------*
* Parâmetros de Seleção
*----------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
PARAMETERS: p_users  AS CHECKBOX DEFAULT 'X',  "Informações de usuários
            p_resp   AS CHECKBOX DEFAULT 'X',  "Tempo de resposta
            p_mem    AS CHECKBOX DEFAULT 'X',  "Uso de memória
            p_conn   AS CHECKBOX DEFAULT 'X',  "Conexões ativas
            p_detl   AS CHECKBOX.              "Detalhamento completo
SELECTION-SCREEN END OF BLOCK b1.

SELECTION-SCREEN BEGIN OF BLOCK b2 WITH FRAME TITLE TEXT-002.
PARAMETERS: p_days TYPE i DEFAULT 1.           "Dias para análise
SELECTION-SCREEN END OF BLOCK b2.

*----------------------------------------------------------------------*
* Inicialização
*----------------------------------------------------------------------*
INITIALIZATION.
  " Textos de seleção
  TEXT-001 = 'Opções de Relatório'.
  TEXT-002 = 'Período de Análise'.

*----------------------------------------------------------------------*
* Evento START-OF-SELECTION
*----------------------------------------------------------------------*
START-OF-SELECTION.

  " Obter timestamp atual
  GET TIME STAMP FIELD lv_timestamp.

  " Cabeçalho do relatório
  PERFORM display_header.

  " 1. Informações de Usuários
  IF p_users = 'X'.
    PERFORM get_user_information.
  ENDIF.

  " 2. Tempo de Resposta
  IF p_resp = 'X'.
    PERFORM get_response_time.
  ENDIF.

  " 3. Uso de Memória
  IF p_mem = 'X'.
    PERFORM get_memory_usage.
  ENDIF.

  " 4. Conexões Ativas
  IF p_conn = 'X'.
    PERFORM get_connection_info.
  ENDIF.

  " Rodapé do relatório
  PERFORM display_footer.

*----------------------------------------------------------------------*
* FORMS
*----------------------------------------------------------------------*

*&---------------------------------------------------------------------*
*& Form display_header
*&---------------------------------------------------------------------*
FORM display_header.
  DATA: lv_date TYPE sy-datum,
        lv_time TYPE sy-uzeit.

  lv_date = sy-datum.
  lv_time = sy-uzeit.

  WRITE: / '═══════════════════════════════════════════════════════════════════════'.
  WRITE: / '          RELATÓRIO DE PERFORMANCE DO SAP HANA'.
  WRITE: / '═══════════════════════════════════════════════════════════════════════'.
  WRITE: / 'Data:', lv_date, '   Hora:', lv_time.
  WRITE: / 'Sistema:', sy-sysid, '   Mandante:', sy-mandt.
  WRITE: / '─────────────────────────────────────────────────────────────────────'.
  SKIP.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form get_user_information
*&---------------------------------------------------------------------*
FORM get_user_information.
  DATA: lv_total   TYPE i,
        lv_logged  TYPE i,
        lv_locked  TYPE i,
        lv_percent TYPE p DECIMALS 2.

  WRITE: / '📊 INFORMAÇÕES DE USUÁRIOS'.
  WRITE: / '─────────────────────────────────────────────────────────────────────'.

  TRY.
      " Chamar método AMDP para obter informações de usuários
      zhana_perf_cl=>get_user_statistics(
        IMPORTING
          ev_total_users  = lv_total
          ev_logged_users = lv_logged
          ev_locked_users = lv_locked
          et_users        = lt_users
      ).

      " Calcular percentual de usuários logados
      IF lv_total > 0.
        lv_percent = ( lv_logged / lv_total ) * 100.
      ENDIF.

      " Exibir resumo
      WRITE: / 'Total de Usuários Cadastrados:', lv_total.
      WRITE: / 'Usuários Atualmente Logados:  ', lv_logged.
      WRITE: / 'Usuários Bloqueados:          ', lv_locked.
      WRITE: / 'Percentual de Uso:            ', lv_percent, '%'.

      IF p_detl = 'X'.
        SKIP.
        WRITE: / 'Detalhamento de Usuários Logados:'.
        WRITE: / '   Usuário    | Sessões | Última Conexão      | Transação'.
        WRITE: / '   -----------|---------|---------------------|----------'.

        LOOP AT lt_users INTO DATA(ls_user).
          WRITE: / '  ', ls_user-username,
                   '|', ls_user-sessions,
                   '|', ls_user-last_login,
                   '|', ls_user-transaction.
        ENDLOOP.
      ENDIF.

    CATCH cx_amdp_execution_error INTO DATA(lx_amdp).
      WRITE: / '❌ Erro ao obter informações de usuários:', lx_amdp->get_text( ).
  ENDTRY.

  SKIP.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form get_response_time
*&---------------------------------------------------------------------*
FORM get_response_time.
  DATA: lv_avg_time TYPE p DECIMALS 3,
        lv_min_time TYPE p DECIMALS 3,
        lv_max_time TYPE p DECIMALS 3.

  WRITE: / '⏱️  TEMPO DE RESPOSTA DO SISTEMA'.
  WRITE: / '─────────────────────────────────────────────────────────────────────'.

  TRY.
      " Chamar método AMDP para obter tempos de resposta
      zhana_perf_cl=>get_response_times(
        EXPORTING
          iv_days        = p_days
        IMPORTING
          ev_avg_time    = lv_avg_time
          ev_min_time    = lv_min_time
          ev_max_time    = lv_max_time
          et_response    = lt_response_time
      ).

      WRITE: / 'Tempo Médio de Resposta:', lv_avg_time, 'ms'.
      WRITE: / 'Tempo Mínimo:           ', lv_min_time, 'ms'.
      WRITE: / 'Tempo Máximo:           ', lv_max_time, 'ms'.

      IF p_detl = 'X' AND lt_response_time IS NOT INITIAL.
        SKIP.
        WRITE: / 'Top 10 Queries Mais Lentas:'.
        WRITE: / '   Ranking | Tempo (ms) | Tipo Query | Statement'.
        WRITE: / '   --------|------------|------------|----------'.

        LOOP AT lt_response_time INTO DATA(ls_resp) TO 10.
          WRITE: / '   ', sy-tabix,
                   '|', ls_resp-response_time,
                   '|', ls_resp-query_type,
                   '|', ls_resp-statement+0(40).
        ENDLOOP.
      ENDIF.

    CATCH cx_amdp_execution_error INTO DATA(lx_amdp).
      WRITE: / '❌ Erro ao obter tempo de resposta:', lx_amdp->get_text( ).
  ENDTRY.

  SKIP.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form get_memory_usage
*&---------------------------------------------------------------------*
FORM get_memory_usage.
  DATA: lv_total_mem  TYPE int8,
        lv_used_mem   TYPE int8,
        lv_free_mem   TYPE int8,
        lv_percent    TYPE p DECIMALS 2.

  WRITE: / '💾 USO DE MEMÓRIA DO HANA'.
  WRITE: / '─────────────────────────────────────────────────────────────────────'.

  TRY.
      " Chamar método AMDP para obter uso de memória
      zhana_perf_cl=>get_memory_statistics(
        IMPORTING
          ev_total_memory = lv_total_mem
          ev_used_memory  = lv_used_mem
          ev_free_memory  = lv_free_mem
          et_memory       = lt_memory_usage
      ).

      " Calcular percentual
      IF lv_total_mem > 0.
        lv_percent = ( lv_used_mem / lv_total_mem ) * 100.
      ENDIF.

      WRITE: / 'Memória Total Alocada: ', lv_total_mem, 'GB'.
      WRITE: / 'Memória Utilizada:     ', lv_used_mem, 'GB'.
      WRITE: / 'Memória Livre:         ', lv_free_mem, 'GB'.
      WRITE: / 'Percentual de Uso:     ', lv_percent, '%'.

      " Alerta de uso crítico
      IF lv_percent > 90.
        WRITE: / '⚠️  ALERTA: Uso de memória acima de 90%!'.
      ELSEIF lv_percent > 80.
        WRITE: / '⚠️  AVISO: Uso de memória acima de 80%.'.
      ENDIF.

      IF p_detl = 'X' AND lt_memory_usage IS NOT INITIAL.
        SKIP.
        WRITE: / 'Detalhamento por Serviço:'.
        WRITE: / '   Serviço        | Memória Usada (GB) | % do Total'.
        WRITE: / '   ---------------|-------------------|----------'.

        LOOP AT lt_memory_usage INTO DATA(ls_mem).
          WRITE: / '  ', ls_mem-service_name,
                   '|', ls_mem-used_memory,
                   '|', ls_mem-percentage, '%'.
        ENDLOOP.
      ENDIF.

    CATCH cx_amdp_execution_error INTO DATA(lx_amdp).
      WRITE: / '❌ Erro ao obter uso de memória:', lx_amdp->get_text( ).
  ENDTRY.

  SKIP.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form get_connection_info
*&---------------------------------------------------------------------*
FORM get_connection_info.
  DATA: lv_total_conn   TYPE i,
        lv_active_conn  TYPE i,
        lv_idle_conn    TYPE i.

  WRITE: / '🔗 CONEXÕES ATIVAS'.
  WRITE: / '─────────────────────────────────────────────────────────────────────'.

  TRY.
      " Chamar método AMDP para obter informações de conexões
      zhana_perf_cl=>get_connection_statistics(
        IMPORTING
          ev_total_connections  = lv_total_conn
          ev_active_connections = lv_active_conn
          ev_idle_connections   = lv_idle_conn
          et_connections        = lt_connections
      ).

      WRITE: / 'Total de Conexões:   ', lv_total_conn.
      WRITE: / 'Conexões Ativas:     ', lv_active_conn.
      WRITE: / 'Conexões Inativas:   ', lv_idle_conn.

      IF p_detl = 'X' AND lt_connections IS NOT INITIAL.
        SKIP.
        WRITE: / 'Conexões Ativas - Top 10:'.
        WRITE: / '   Host       | Port  | Status | Usuário    | Aplicação'.
        WRITE: / '   -----------|-------|--------|------------|----------'.

        LOOP AT lt_connections INTO DATA(ls_conn) TO 10.
          WRITE: / '  ', ls_conn-host,
                   '|', ls_conn-port,
                   '|', ls_conn-status,
                   '|', ls_conn-user,
                   '|', ls_conn-application.
        ENDLOOP.
      ENDIF.

    CATCH cx_amdp_execution_error INTO DATA(lx_amdp).
      WRITE: / '❌ Erro ao obter informações de conexões:', lx_amdp->get_text( ).
  ENDTRY.

  SKIP.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form display_footer
*&---------------------------------------------------------------------*
FORM display_footer.
  WRITE: / '═══════════════════════════════════════════════════════════════════════'.
  WRITE: / '                    FIM DO RELATÓRIO'.
  WRITE: / '═══════════════════════════════════════════════════════════════════════'.
ENDFORM.
