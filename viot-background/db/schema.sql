-- Device data
CREATE TABLE device_data (
    device_id UUID NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    key TEXT NOT NULL,
    bool_v BOOLEAN,
    str_v TEXT,
    long_v BIGINT,
    double_v DOUBLE PRECISION,
    json_v JSON,
    PRIMARY KEY (device_id, ts, key)
);

-- Device attribute
CREATE TABLE device_attribute (
    device_id UUID NOT NULL,
    key TEXT NOT NULL,
    scope SMALLINT NOT NULL,
    last_update TIMESTAMPTZ NOT NULL,
    bool_v BOOLEAN,
    str_v TEXT,
    long_v BIGINT,
    double_v DOUBLE PRECISION,
    json_v JSONB,
    PRIMARY KEY (device_id, key)
)
