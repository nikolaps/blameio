CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE table_io (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    db TEXT,
    table_name TEXT,
    FETCH_LATENCY DOUBLE PRECISION,
    INSERT_LATENCY DOUBLE PRECISION,
    UPDATE_LATENCY DOUBLE PRECISION,
    DELETE_LATENCY DOUBLE PRECISION,
    COUNT_STAR BIGINT,
    WAIT_LATENCY DOUBLE PRECISION
);

CREATE INDEX idx_table_io_time_table_name
ON table_io (time, table_name);

CREATE TABLE index_io (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    db TEXT,
    index_name TEXT,
    FETCH_LATENCY DOUBLE PRECISION,
    INSERT_LATENCY DOUBLE PRECISION,
    UPDATE_LATENCY DOUBLE PRECISION,
    DELETE_LATENCY DOUBLE PRECISION,
    COUNT_STAR BIGINT,
    WAIT_LATENCY DOUBLE PRECISION
);

CREATE INDEX idx_index_io_time_idx_name
ON index_io (time, index_name);

CREATE TABLE digest_stats (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    id BIGINT,
    "user" TEXT,
    host TEXT,
    db TEXT,
    command TEXT,
    exec_time BIGINT NOT NULL,
    query TEXT,
    state TEXT,
    trx_state TEXT,
    trx_operation_state TEXT,
    trx_rows_locked BIGINT,
    trx_rows_modified BIGINT
);

CREATE TABLE replication (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    db TEXT,
    host TEXT,
    Master_Log_File TEXT,
    Read_Master_Log_Pos BIGINT,
    Relay_Master_Log_File TEXT,
    Exec_Master_Log_Pos BIGINT,
    Seconds_Behind_Master BIGINT
);

SELECT create_hypertable('table_io', 'time', chunk_time_interval => interval '15 minutes');
SELECT create_hypertable('index_io', 'time', chunk_time_interval => interval '15 minutes');
SELECT create_hypertable('digest_stats', 'time', chunk_time_interval => interval '15 minutes');
SELECT create_hypertable('replication', 'time', chunk_time_interval => interval '15 minutes');

ALTER TABLE table_io SET (timescaledb.compress, timescaledb.compress_segmentby = 'db,table_name');
ALTER TABLE index_io SET (timescaledb.compress, timescaledb.compress_segmentby = 'db,index_name');
ALTER TABLE digest_stats SET (timescaledb.compress, timescaledb.compress_segmentby = 'db');
ALTER TABLE replication SET (timescaledb.compress, timescaledb.compress_segmentby = 'db,host');

SELECT add_compression_policy('table_io', interval '30 minutes');
SELECT add_compression_policy('index_io', interval '30 minutes');
SELECT add_compression_policy('digest_stats', interval '30 minutes');
SELECT add_compression_policy('replication', interval '30 minutes');

SELECT add_retention_policy('table_io', INTERVAL '1 week');
SELECT add_retention_policy('index_io', INTERVAL '1 week');
SELECT add_retention_policy('digest_stats', INTERVAL '1 week');
SELECT add_retention_policy('replication', INTERVAL '1 week');
