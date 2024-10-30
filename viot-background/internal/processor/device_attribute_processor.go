package processor

import (
	"context"
	"fmt"
	"time"

	"github.com/goccy/go-json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"go.uber.org/zap"

	"github.com/vuxmai/viot/viot-background/db/repository"
	"github.com/vuxmai/viot/viot-background/pkg/config"
)

type deviceAttributeMsg struct {
	DeviceId  string                 `json:"device_id"`
	Data      map[string]interface{} `json:"attributes"`
}

type deviceAttributeProcessor struct {
	payloadQueue chan []byte
	paramQueue   chan repository.BatchUpsertDeviceAttributeParams
	quitCh       chan bool
	logger       *zap.Logger
}

func NewDeviceAttributeProcessor(payloadQueue chan []byte, logger *zap.Logger) *deviceAttributeProcessor {
	return &deviceAttributeProcessor{
		payloadQueue: payloadQueue,
		paramQueue:   make(chan repository.BatchUpsertDeviceAttributeParams),
		quitCh:       make(chan bool),
		logger:       logger,
	}
}

func (p *deviceAttributeProcessor) Start(ctx context.Context, cfg *config.DeviceAttributeProcessorConfig, store repository.Store) {
	p.logger.Info("Device attribute Processor starting")

	go p.convertWorker(ctx)
	go p.batchUpsertWorker(ctx, cfg, store)
}

func (p *deviceAttributeProcessor) convertWorker(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return

		case payload := <-p.payloadQueue:
			var msg deviceAttributeMsg
			if err := json.Unmarshal(payload, &msg); err != nil {
				p.logger.Warn("failed to unmarshal device attribute msg", zap.Error(err))
				continue
			}

			batchParams, err := convertDeviceAttributeMsgToBatchParams(msg)
			if err != nil {
				p.logger.Error("failed to convert device attribute msg to batch params", zap.Error(err))
				continue
			}

			for _, param := range batchParams {
				p.paramQueue <- param
			}

		case <-p.quitCh:
			p.logger.Info("DeviceDataWorker stopping")
			return
		}
	}
}

func (p *deviceAttributeProcessor) batchUpsertWorker(ctx context.Context, cfg *config.DeviceAttributeProcessorConfig, store repository.Store) {
	ticker := time.NewTicker(time.Duration(cfg.MaxBatchIntervalMs * int(time.Millisecond)))
	defer ticker.Stop()

	batch := []repository.BatchUpsertDeviceAttributeParams{}

	for {
		select {
		case <-ctx.Done():
			return

		case param := <-p.paramQueue:
			batch = append(batch, param)
			if len(batch) >= cfg.MaxBatchSize {
				go processDeviceAttributeBatch(ctx, store, batch, p.logger)
				batch = nil
			}

		case <-ticker.C:
			go processDeviceAttributeBatch(ctx, store, batch, p.logger)
			batch = nil

		case <-p.quitCh:
			go processDeviceAttributeBatch(ctx, store, batch, p.logger)
			batch = nil
			return
		}
	}
}

func convertDeviceAttributeMsgToBatchParams(msg deviceAttributeMsg) ([]repository.BatchUpsertDeviceAttributeParams, error) {
	batchParams := []repository.BatchUpsertDeviceAttributeParams{}

	deviceUUID, err := uuid.Parse(msg.DeviceId)
	if err != nil {
		return nil, fmt.Errorf("failed to set UUID: %w", err)
	}

	ts := pgtype.Timestamptz{Time: time.Now(), Valid: true}

	for key, value := range msg.Data {
		param := repository.BatchUpsertDeviceAttributeParams{
			DeviceID:   deviceUUID,
			LastUpdate: ts,
			Key:        key,
			Scope:      repository.ClientScope,
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

func processDeviceAttributeBatch(ctx context.Context, store repository.Store, batch []repository.BatchUpsertDeviceAttributeParams, logger *zap.Logger) {
	if len(batch) == 0 {
		return
	}

	err := store.BatchUpsertDeviceAttribute(ctx, batch)
	if err != nil {
		logger.Error("failed to batch upsert device attribute", zap.Error(err))
	}
}
