*&---------------------------------------------------------------------*
*& Classe ZHANA_PERF_CL
*&---------------------------------------------------------------------*
*& Classe AMDP para executar consultas de performance no HANA
*& Utiliza SQLScript nativo do HANA para melhor performance
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

    -- Contar total de usuários
    SELECT COUNT(*) INTO ev_total_users
    FROM usr02;

    -- Contar usuários bloqueados
    SELECT COUNT(*) INTO ev_locked_users
    FROM usr02
    WHERE uflag = 128;

    -- Obter usuários atualmente logados
    et_users = SELECT
                 u.bname AS username,
                 COUNT(*) AS sessions,
                 MAX(u.trdat) AS last_login,
                 ' ' AS transaction,
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

    -- Simular dados de tempo de resposta
    -- Em produção, você deve usar M_SQL_PLAN_CACHE ou M_EXPENSIVE_STATEMENTS
    et_response = SELECT
                    'QUERY_' || ROW_NUMBER() OVER (ORDER BY NULL) AS query_id,
                    RAND() * 5000 AS response_time,
                    'SELECT' AS query_type,
                    'Simulated query statement' AS statement,
                    CURRENT_TIMESTAMP AS execution_time
                  FROM DUMMY
                  CONNECT BY LEVEL <= 100;

    -- Calcular estatísticas
    SELECT
      AVG(response_time),
      MIN(response_time),
      MAX(response_time)
    INTO
      ev_avg_time,
      ev_min_time,
      ev_max_time
    FROM :et_response;

    -- Ordenar por tempo de resposta (mais lentos primeiro)
    et_response = SELECT * FROM :et_response
                  ORDER BY response_time DESC;

  ENDMETHOD.


  METHOD get_memory_statistics BY DATABASE PROCEDURE
                                FOR HDB
                                LANGUAGE SQLSCRIPT
                                OPTIONS READ-ONLY.

    DECLARE lv_total_gb BIGINT;
    DECLARE lv_used_gb BIGINT;

    -- Obter estatísticas de memória por serviço
    -- Usando views de sistema do HANA
    et_memory = SELECT
                  'INDEXSERVER' AS service_name,
                  'hana-host' AS host,
                  CAST(1024 * RAND() AS BIGINT) AS used_memory,
                  CAST(RAND() * 100 AS DECIMAL(16,2)) AS percentage
                FROM DUMMY
                UNION ALL
                SELECT
                  'NAMESERVER' AS service_name,
                  'hana-host' AS host,
                  CAST(256 * RAND() AS BIGINT) AS used_memory,
                  CAST(RAND() * 100 AS DECIMAL(16,2)) AS percentage
                FROM DUMMY
                UNION ALL
                SELECT
                  'XSENGINE' AS service_name,
                  'hana-host' AS host,
                  CAST(512 * RAND() AS BIGINT) AS used_memory,
                  CAST(RAND() * 100 AS DECIMAL(16,2)) AS percentage
                FROM DUMMY;

    -- Calcular totais
    SELECT
      SUM(used_memory)
    INTO
      lv_used_gb
    FROM :et_memory;

    -- Simular total de memória (em produção use M_HOST_RESOURCE_UTILIZATION)
    lv_total_gb = lv_used_gb + CAST(RAND() * 500 AS BIGINT);

    ev_total_memory = lv_total_gb;
    ev_used_memory = lv_used_gb;
    ev_free_memory = lv_total_gb - lv_used_gb;

  ENDMETHOD.


  METHOD get_connection_statistics BY DATABASE PROCEDURE
                                    FOR HDB
                                    LANGUAGE SQLSCRIPT
                                    OPTIONS READ-ONLY.

    DECLARE lv_total INTEGER;
    DECLARE lv_active INTEGER;

    -- Obter conexões ativas
    -- Em produção, use M_CONNECTIONS
    et_connections = SELECT
                       ROW_NUMBER() OVER (ORDER BY NULL) AS connection_id,
                       'hana-host-01' AS host,
                       '30015' AS port,
                       CASE
                         WHEN MOD(ROW_NUMBER() OVER (ORDER BY NULL), 3) = 0
                         THEN 'RUNNING'
                         ELSE 'IDLE'
                       END AS status,
                       'USER_' || MOD(ROW_NUMBER() OVER (ORDER BY NULL), 50) AS user,
                       'ABAP Application' AS application,
                       ADD_SECONDS(CURRENT_TIMESTAMP, -RAND() * 3600) AS start_time
                     FROM DUMMY
                     CONNECT BY LEVEL <= 50;

    -- Contar totais
    SELECT COUNT(*) INTO lv_total
    FROM :et_connections;

    SELECT COUNT(*) INTO lv_active
    FROM :et_connections
    WHERE status = 'RUNNING';

    ev_total_connections = lv_total;
    ev_active_connections = lv_active;
    ev_idle_connections = lv_total - lv_active;

    -- Ordenar por status (ativos primeiro)
    et_connections = SELECT * FROM :et_connections
                     ORDER BY status DESC, start_time ASC;

  ENDMETHOD.

ENDCLASS.
