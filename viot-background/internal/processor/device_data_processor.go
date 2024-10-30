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

type deviceDataMsg struct {
	DeviceId  string                 `json:"device_id"`
	TimeStamp time.Time              `json:"ts"`
	Data      map[string]interface{} `json:"data"`
}

type deviceDataProcessor struct {
	payloadQueue chan []byte
	paramQueue   chan repository.BatchInsertDeviceDataParam
	quitCh       chan bool
	logger       *zap.Logger
}

func NewDeviceDataProcessor(payloadQueue chan []byte, logger *zap.Logger) *deviceDataProcessor {
	return &deviceDataProcessor{
		payloadQueue: payloadQueue,
		paramQueue:   make(chan repository.BatchInsertDeviceDataParam),
		quitCh:       make(chan bool),
		logger:       logger,
	}
}

func (p *deviceDataProcessor) Start(ctx context.Context, cfg *config.DeviceDataProcessorConfig, store repository.Store) {
	p.logger.Info("Device data Processor starting")

	go p.convertWorker(ctx)
	go p.batchInsertWorker(ctx, cfg, store)
}

func (p *deviceDataProcessor) convertWorker(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return

		case payload := <-p.payloadQueue:
			var msg deviceDataMsg
			if err := json.Unmarshal(payload, &msg); err != nil {
				p.logger.Warn("failed to unmarshal device data msg", zap.Error(err))
				continue
			}

			batch, err := convertDeviceDataMsgToBatchParams(msg)
			if err != nil {
				p.logger.Warn("failed to convert device data msg", zap.Error(err))
				continue
			}

			for _, param := range batch {
				p.paramQueue <- param
			}

		case <-p.quitCh:
			p.logger.Info("DeviceDataWorker stopping")
			return
		}
	}
}

func (p *deviceDataProcessor) batchInsertWorker(ctx context.Context, cfg *config.DeviceDataProcessorConfig, store repository.Store) {
	ticker := time.NewTicker(time.Duration(cfg.MaxBatchIntervalMs * int(time.Millisecond)))
	defer ticker.Stop()

	var batch []repository.BatchInsertDeviceDataParam

	for {
		select {
		case <-ctx.Done():
			return

		case param := <-p.paramQueue:
			batch = append(batch, param)
			if len(batch) >= cfg.MaxBatchSize {
				go processBatch(ctx, store, batch, p.logger)
				batch = nil
			}

		case <-ticker.C:
			go processBatch(ctx, store, batch, p.logger)
			batch = nil

		case <-p.quitCh:
			go processBatch(ctx, store, batch, p.logger)
			batch = nil
			return
		}
	}
}

func convertDeviceDataMsgToBatchParams(msg deviceDataMsg) ([]repository.BatchInsertDeviceDataParam, error) {
	batchParams := []repository.BatchInsertDeviceDataParam{}

	deviceUUID, err := uuid.Parse(msg.DeviceId)
	if err != nil {
		return nil, fmt.Errorf("failed to set UUID: %w", err)
	}

	ts := pgtype.Timestamptz{Time: msg.TimeStamp, Valid: true}

	for key, value := range msg.Data {
		param := repository.BatchInsertDeviceDataParam{
			DeviceID: deviceUUID,
			Ts:       ts,
			Key:      key,
		}

		if err := setParamValue(&param, value); err != nil {
			return nil, err
		}
		batchParams = append(batchParams, param)
	}

	return batchParams, nil
}

func processBatch(ctx context.Context, store repository.Store, batch []repository.BatchInsertDeviceDataParam, logger *zap.Logger) {
	if len(batch) == 0 {
		return
	}

	if err := store.BatchInsertDeviceData(ctx, batch); err != nil {
		logger.Error("Error inserting batch", zap.Error(err))
	}
}
