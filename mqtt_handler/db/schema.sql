-- Device data
CREATE TABLE device_data (
    device_id UUID NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    key TEXT NOT NULL,
    bool_v BOOLEAN,
    str_v TEXT,
    long_v BIGINT,
    double_v DOUBLE PRECISION,
    json_v JSONB,
    PRIMARY KEY (device_id, ts, key)
);
