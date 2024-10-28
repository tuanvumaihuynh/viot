package repository

import "context"

func (s *SQLStore) BatchInsertDeviceDataTx(ctx context.Context, data []BatchInsertDeviceDataParams) error {
	return s.execTx(ctx, func(q *Queries) error {
		return q.BatchInsertDeviceData(ctx, data)
	})
}
