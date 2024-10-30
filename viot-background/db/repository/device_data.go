package repository

import (
	"context"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgtype"
)

const batchInsertDeviceData = `
INSERT INTO device_data (device_id, ts, key, bool_v, str_v, long_v, double_v, json_v)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT (device_id, ts, key)
DO NOTHING;
`

type BatchInsertDeviceDataParam struct {
	DeviceID uuid.UUID
	Ts       pgtype.Timestamptz
	Key      string
	BoolV    *bool
	StrV     *string
	LongV    *int
	DoubleV  *float64
	JsonV    map[string]interface{}
}

func (p *BatchInsertDeviceDataParam) SetBoolV(v *bool)                  { p.BoolV = v }
func (p *BatchInsertDeviceDataParam) SetStrV(v *string)                 { p.StrV = v }
func (p *BatchInsertDeviceDataParam) SetLongV(v *int)                   { p.LongV = v }
func (p *BatchInsertDeviceDataParam) SetDoubleV(v *float64)             { p.DoubleV = v }
func (p *BatchInsertDeviceDataParam) SetJsonV(v map[string]interface{}) { p.JsonV = v }

func (q *Queries) BatchInsertDeviceData(ctx context.Context, arg []BatchInsertDeviceDataParam) error {
	batch := &pgx.Batch{}
	for _, a := range arg {
		vals := []interface{}{
			a.DeviceID,
			a.Ts,
			a.Key,
			a.BoolV,
			a.StrV,
			a.LongV,
			a.DoubleV,
			a.JsonV,
		}
		batch.Queue(batchInsertDeviceData, vals...)
	}
	br := q.db.SendBatch(ctx, batch)
	defer br.Close()

	for t := 0; t < len(arg); t++ {
		_, err := br.Exec()
		if err != nil {
			return fmt.Errorf("error inserting record %d: %w", t, err)
		}
	}
	return nil
}
