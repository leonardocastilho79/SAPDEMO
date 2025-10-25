*&---------------------------------------------------------------------*
*& Classe ZHANA_PERF_CL (VERSÃO PRODUÇÃO)
*&---------------------------------------------------------------------*
*& Classe AMDP com queries reais usando views de sistema do HANA
*& Use esta versão em ambiente de produção SAP HANA
*&---------------------------------------------------------------------*
CLASS zhana_perf_cl DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.

    " Tipos de estrutura para retorno de dados
    TYPES: BEGIN OF ty_user_info,
             username     TYPE char40,
             sessions     TYPE i,
             last_login   TYPE timestamp,
             transaction  TYPE char20,
             status       TYPE char10,
           END OF ty_user_info.

    TYPES: BEGIN OF ty_response_time,
             query_id       TYPE char32,
             response_time  TYPE p LENGTH 16 DECIMALS 3,
             query_type     TYPE char20,
             statement      TYPE string,
             execution_time TYPE timestamp,
           END OF ty_response_time.

    TYPES: BEGIN OF ty_memory_usage,
             service_name  TYPE char50,
             host          TYPE char50,
             used_memory   TYPE int8,
             percentage    TYPE p LENGTH 16 DECIMALS 2,
           END OF ty_memory_usage.

    TYPES: BEGIN OF ty_connection_info,
             connection_id TYPE i,
             host          TYPE char50,
             port          TYPE char10,
             status        TYPE char20,
             user          TYPE char40,
             application   TYPE char50,
             start_time    TYPE timestamp,
           END OF ty_connection_info.

    " Métodos públicos
    CLASS-METHODS:
      get_user_statistics
        EXPORTING
          VALUE(ev_total_users)  TYPE i
          VALUE(ev_logged_users) TYPE i
          VALUE(ev_locked_users) TYPE i
          VALUE(et_users)        TYPE STANDARD TABLE,

      get_response_times
        IMPORTING
          VALUE(iv_days)    TYPE i DEFAULT 1
        EXPORTING
          VALUE(ev_avg_time) TYPE p
          VALUE(ev_min_time) TYPE p
          VALUE(ev_max_time) TYPE p
          VALUE(et_response) TYPE STANDARD TABLE,

      get_memory_statistics
        EXPORTING
          VALUE(ev_total_memory) TYPE int8
          VALUE(ev_used_memory)  TYPE int8
          VALUE(ev_free_memory)  TYPE int8
          VALUE(et_memory)       TYPE STANDARD TABLE,

      get_connection_statistics
        EXPORTING
          VALUE(ev_total_connections)  TYPE i
          VALUE(ev_active_connections) TYPE i
          VALUE(ev_idle_connections)   TYPE i
          VALUE(et_connections)        TYPE STANDARD TABLE.

  PROTECTED SECTION.
  PRIVATE SECTION.

ENDCLASS.



CLASS zhana_perf_cl IMPLEMENTATION.

  METHOD get_user_statistics BY DATABASE PROCEDURE
                              FOR HDB
                              LANGUAGE SQLSCRIPT
                              OPTIONS READ-ONLY
                              USING usr02 usr41.

    -- Contar total de usuários cadastrados
    SELECT COUNT(*) INTO ev_total_users
    FROM usr02;

    -- Contar usuários bloqueados
    SELECT COUNT(*) INTO ev_locked_users
    FROM usr02
    WHERE uflag = 128;

    -- Obter usuários atualmente logados
    -- Usar tabela USR41 para sessões ativas
    et_users = SELECT
                 u.bname AS username,
                 COUNT(*) AS sessions,
                 MAX(TIMESTAMP(u.trdat, u.ltime)) AS last_login,
                 MAX(u.last_transaction) AS transaction,
                 CASE
                   WHEN u.uflag = 0 THEN 'ATIVO'
                   WHEN u.uflag = 128 THEN 'BLOQUEADO'
                   ELSE 'OUTRO'
                 END AS status
               FROM usr02 AS u
               WHERE u.trdat >= ADD_DAYS(CURRENT_DATE, -1)
               GROUP BY u.bname, u.uflag
               ORDER BY sessions DESC;

    -- Contar usuários logados
    SELECT COUNT(*) INTO ev_logged_users
    FROM :et_users;

  ENDMETHOD.


  METHOD get_response_times BY DATABASE PROCEDURE
                             FOR HDB
                             LANGUAGE SQLSCRIPT
                             OPTIONS READ-ONLY.

    DECLARE lv_start_time TIMESTAMP;
    DECLARE lv_cutoff_days INTEGER;

    lv_cutoff_days = :iv_days;
    lv_start_time = ADD_DAYS(CURRENT_TIMESTAMP, -:lv_cutoff_days);

    /*
     * Usando M_SQL_PLAN_CACHE para obter queries reais
     * Esta view contém todas as queries em cache com estatísticas
     */
    et_response = SELECT TOP 1000
                    STATEMENT_HASH AS query_id,
                    CAST(TOTAL_EXECUTION_TIME / EXECUTION_COUNT AS DECIMAL(16,3)) AS response_time,
                    CASE
                      WHEN STATEMENT_STRING LIKE 'SELECT%' THEN 'SELECT'
                      WHEN STATEMENT_STRING LIKE 'INSERT%' THEN 'INSERT'
                      WHEN STATEMENT_STRING LIKE 'UPDATE%' THEN 'UPDATE'
                      WHEN STATEMENT_STRING LIKE 'DELETE%' THEN 'DELETE'
                      ELSE 'OTHER'
                    END AS query_type,
                    SUBSTR(STATEMENT_STRING, 1, 1000) AS statement,
                    LAST_EXECUTION_TIMESTAMP AS execution_time
                  FROM M_SQL_PLAN_CACHE
                  WHERE LAST_EXECUTION_TIMESTAMP >= :lv_start_time
                    AND EXECUTION_COUNT > 0
                    AND TOTAL_EXECUTION_TIME > 0
                  ORDER BY response_time DESC;

    -- Calcular estatísticas de tempo
    SELECT
      AVG(response_time),
      MIN(response_time),
      MAX(response_time)
    INTO
      ev_avg_time,
      ev_min_time,
      ev_max_time
    FROM :et_response;

  ENDMETHOD.


  METHOD get_memory_statistics BY DATABASE PROCEDURE
                                FOR HDB
                                LANGUAGE SQLSCRIPT
                                OPTIONS READ-ONLY.

    DECLARE lv_total_bytes BIGINT;
    DECLARE lv_used_bytes BIGINT;
    DECLARE lv_free_bytes BIGINT;

    /*
     * Usando M_SERVICE_MEMORY para estatísticas reais de memória
     * Esta view fornece uso de memória por serviço HANA
     */
    et_memory = SELECT
                  SERVICE_NAME AS service_name,
                  HOST AS host,
                  CAST(USED_MEMORY_SIZE / 1024 / 1024 / 1024 AS BIGINT) AS used_memory,
                  CAST((USED_MEMORY_SIZE * 100.0 / TOTAL_MEMORY_USED_SIZE) AS DECIMAL(16,2)) AS percentage
                FROM M_SERVICE_MEMORY
                WHERE TOTAL_MEMORY_USED_SIZE > 0
                ORDER BY used_memory DESC;

    /*
     * Usar M_HOST_RESOURCE_UTILIZATION para memória total do sistema
     */
    SELECT
      CAST(SUM(INSTANCE_TOTAL_MEMORY_ALLOCATED_SIZE) / 1024 / 1024 / 1024 AS BIGINT),
      CAST(SUM(INSTANCE_TOTAL_MEMORY_USED_SIZE) / 1024 / 1024 / 1024 AS BIGINT)
    INTO
      lv_total_bytes,
      lv_used_bytes
    FROM M_HOST_RESOURCE_UTILIZATION;

    lv_free_bytes = lv_total_bytes - lv_used_bytes;

    ev_total_memory = lv_total_bytes;
    ev_used_memory = lv_used_bytes;
    ev_free_memory = lv_free_bytes;

  ENDMETHOD.


  METHOD get_connection_statistics BY DATABASE PROCEDURE
                                    FOR HDB
                                    LANGUAGE SQLSCRIPT
                                    OPTIONS READ-ONLY.

    DECLARE lv_total INTEGER;
    DECLARE lv_active INTEGER;
    DECLARE lv_idle INTEGER;

    /*
     * Usando M_CONNECTIONS para obter conexões reais do HANA
     * Esta view mostra todas as conexões ativas no banco
     */
    et_connections = SELECT
                       CONNECTION_ID AS connection_id,
                       HOST AS host,
                       PORT AS port,
                       CONNECTION_STATUS AS status,
                       USER_NAME AS user,
                       CLIENT_APPLICATION AS application,
                       START_TIME AS start_time
                     FROM M_CONNECTIONS
                     WHERE CONNECTION_STATUS IN ('RUNNING', 'IDLE', 'QUEUEING')
                     ORDER BY
                       CASE CONNECTION_STATUS
                         WHEN 'RUNNING' THEN 1
                         WHEN 'QUEUEING' THEN 2
                         WHEN 'IDLE' THEN 3
                         ELSE 4
                       END,
                       START_TIME ASC;

    -- Contar total de conexões
    SELECT COUNT(*) INTO lv_total
    FROM :et_connections;

    -- Contar conexões ativas (RUNNING)
    SELECT COUNT(*) INTO lv_active
    FROM :et_connections
    WHERE status = 'RUNNING';

    -- Calcular conexões idle
    lv_idle = lv_total - lv_active;

    ev_total_connections = lv_total;
    ev_active_connections = lv_active;
    ev_idle_connections = lv_idle;

  ENDMETHOD.

ENDCLASS.
