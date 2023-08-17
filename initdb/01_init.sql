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

CREATE TABLE digest_stats (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    db TEXT,
    digest TEXT,
    query_text TEXT,
    COUNT_STAR BIGINT,
    latency BIGINT,
    SUM_NO_INDEX_USED BIGINT,
    SUM_SELECT_SCAN BIGINT
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
SELECT create_hypertable('digest_stats', 'time', chunk_time_interval => interval '15 minutes');
SELECT create_hypertable('replication', 'time', chunk_time_interval => interval '15 minutes');

ALTER TABLE table_io SET (timescaledb.compress, timescaledb.compress_segmentby = 'db,table_name');
ALTER TABLE digest_stats SET (timescaledb.compress, timescaledb.compress_segmentby = 'db,digest');
ALTER TABLE replication SET (timescaledb.compress, timescaledb.compress_segmentby = 'db,host');

SELECT add_compression_policy('table_io', interval '30 minutes');
SELECT add_compression_policy('digest_stats', interval '30 minutes');
SELECT add_compression_policy('replication', interval '30 minutes');
