package processor

import (
	"context"
	"fmt"
	"time"

	"github.com/goccy/go-json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"go.uber.org/zap"

	"github.com/vuxmai/viot/mqtt_handler/db/repository"
	"github.com/vuxmai/viot/mqtt_handler/pkg/config"
)

type deviceDataMsg struct {
	DeviceId  string                 `json:"device_id"`
	TimeStamp time.Time              `json:"ts"`
	Data      map[string]interface{} `json:"data"`
}

type deviceDataProcessor struct {
	payloadQueue chan []byte
	paramQueue   chan repository.BatchInsertDeviceDataParams
	quitCh       chan bool
	logger       *zap.Logger
}

func NewDeviceDataProcessor(payloadQueue chan []byte, logger *zap.Logger) *deviceDataProcessor {
	return &deviceDataProcessor{
		payloadQueue: payloadQueue,
		paramQueue:   make(chan repository.BatchInsertDeviceDataParams),
		quitCh:       make(chan bool),
		logger:       logger,
	}
}

func (w *deviceDataProcessor) Start(ctx context.Context, cfg *config.DeviceDataProcessorConfig, store repository.Store) {
	w.logger.Info("Device data Processor starting")

	go w.convertWorker(ctx)
	go w.batchInsertWorker(ctx, cfg, store)
}

func (w *deviceDataProcessor) convertWorker(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return

		case payload := <-w.payloadQueue:
			var msg deviceDataMsg
			if err := json.Unmarshal(payload, &msg); err != nil {
				w.logger.Warn("failed to unmarshal device data msg", zap.Error(err))
				continue
			}

			batch, err := convertDeviceDataMsgToBatchParams(msg)
			if err != nil {
				w.logger.Warn("failed to convert device data msg", zap.Error(err))
				continue
			}

			for _, param := range batch {
				w.paramQueue <- param
			}

		case <-w.quitCh:
			w.logger.Info("DeviceDataWorker stopping")
			return
		}
	}
}

func (w *deviceDataProcessor) batchInsertWorker(ctx context.Context, cfg *config.DeviceDataProcessorConfig, store repository.Store) {
	ticker := time.NewTicker(time.Duration(cfg.MaxBatchIntervalMs * int(time.Millisecond)))
	defer ticker.Stop()

	var batch []repository.BatchInsertDeviceDataParams

	for {
		select {
		case <-ctx.Done():
			return

		case param := <-w.paramQueue:
			batch = append(batch, param)
			if len(batch) >= cfg.MaxBatchSize {
				go processBatch(ctx, store, batch, w.logger)
				batch = nil
			}

		case <-ticker.C:
			go processBatch(ctx, store, batch, w.logger)
			batch = nil

		case <-w.quitCh:
			go processBatch(ctx, store, batch, w.logger)
			batch = nil
			return
		}
	}
}

func convertDeviceDataMsgToBatchParams(msg deviceDataMsg) ([]repository.BatchInsertDeviceDataParams, error) {
	batchParams := []repository.BatchInsertDeviceDataParams{}

	deviceUUID, err := uuid.Parse(msg.DeviceId)
	if err != nil {
		return nil, fmt.Errorf("failed to set UUID: %w", err)
	}

	ts := pgtype.Timestamptz{Time: msg.TimeStamp, Valid: true}

	for key, value := range msg.Data {
		param := repository.BatchInsertDeviceDataParams{
			DeviceID: deviceUUID,
			Ts:       ts,
			Key:      key,
		}

		switch v := value.(type) {
		case bool:
			param.BoolV = &v
		case string:
			param.StrV = &v
		case int:
			param.LongV = &v
		case float32, float64:
			floatValue := float64(v.(float64))
			param.DoubleV = &floatValue
		case map[string]interface{}:
			param.JsonV = v
		default:
			return nil, fmt.Errorf("unsupported data type: %T", v)
		}

		batchParams = append(batchParams, param)
	}

	return batchParams, nil
}

func processBatch(ctx context.Context, store repository.Store, batch []repository.BatchInsertDeviceDataParams, logger *zap.Logger) {
	if len(batch) == 0 {
		return
	}

	if err := store.BatchInsertDeviceData(ctx, batch); err != nil {
		logger.Error("Error inserting batch", zap.Error(err))
	}
}
