package repository

import (
	"context"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgtype"
)

type ScopeType int

const (
	ServerScope ScopeType = iota // SERVER_SCOPE = 0
	SharedScope                  // SHARED_SCOPE = 1
	ClientScope                  // CLIENT_SCOPE = 2
)

const batchUpsertDeviceAttribute = `
INSERT INTO device_attribute (device_id, key, scope, last_update, bool_v, str_v, long_v, double_v, json_v)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
ON CONFLICT (device_id, key, scope)
DO UPDATE SET
    last_update = EXCLUDED.last_update,
    bool_v = EXCLUDED.bool_v,
    str_v = EXCLUDED.str_v,
    long_v = EXCLUDED.long_v,
    double_v = EXCLUDED.double_v,
    json_v = EXCLUDED.json_v
WHERE
    device_attribute.bool_v != EXCLUDED.bool_v OR
    device_attribute.str_v != EXCLUDED.str_v OR
    device_attribute.long_v != EXCLUDED.long_v OR
    device_attribute.double_v != EXCLUDED.double_v OR
    CAST(device_attribute.json_v AS TEXT) != CAST(EXCLUDED.json_v AS TEXT);
`

type BatchUpsertDeviceAttributeParams struct {
	DeviceID   uuid.UUID
	Key        string
	Scope      ScopeType
	LastUpdate pgtype.Timestamptz
	BoolV      *bool
	StrV       *string
	LongV      *int
	DoubleV    *float64
	JsonV      map[string]interface{}
}

func (q *Queries) BatchUpsertDeviceAttribute(ctx context.Context, arg []BatchUpsertDeviceAttributeParams) error {
	batch := &pgx.Batch{}
	for _, a := range arg {
		vals := []interface{}{
			a.DeviceID,
			a.Key,
			a.Scope,
			a.LastUpdate,
			a.BoolV,
			a.StrV,
			a.LongV,
			a.DoubleV,
			a.JsonV,
		}
		batch.Queue(batchUpsertDeviceAttribute, vals...)
	}
	br := q.db.SendBatch(ctx, batch)
	defer br.Close()

	for t := 0; t < len(arg); t++ {
		_, err := br.Exec()
		if err != nil {
			return fmt.Errorf("error updating record %d: %w", t, err)
		}
	}
	return nil
}
