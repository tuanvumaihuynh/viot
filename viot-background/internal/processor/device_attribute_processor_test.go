package processor

import (
	"bytes"
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"

	mockdb "github.com/vuxmai/viot/viot-background/db/mock"
	"github.com/vuxmai/viot/viot-background/db/repository"
	"github.com/vuxmai/viot/viot-background/pkg/config"
)

const (
	DeviceAttributeMaxBatchSize       = 2
	DeviceAttributeMaxBatchIntervalMs = 10
)

func defaultDeviceAttributeProcessorConfig() *config.DeviceAttributeProcessorConfig {
	return &config.DeviceAttributeProcessorConfig{
		MaxBatchSize:       DeviceAttributeMaxBatchSize,
		MaxBatchIntervalMs: DeviceAttributeMaxBatchIntervalMs,
	}
}
func TestConvertDeviceAttributeMsgToBatchParams(t *testing.T) {
	attributes := map[string]interface{}{
		"long_value":   100000000000000000,
		"double_value": 22.5,
		"bool_value":   true,
		"str_value":    "sensor1",
		"json_value": map[string]interface{}{
			"key1": "value1",
			"key2": "value2",
		},
	}

	msg := deviceAttributeMsg{
		DeviceId:  uuid.New().String(),
		TimeStamp: time.Now(),
		Data:      attributes,
	}

	params, err := convertDeviceAttributeMsgToBatchParams(msg)

	assert.NoError(t, err)
	assert.Len(t, params, 5)

	for _, param := range params {
		expectedValue, exists := attributes[param.Key]
		if !exists {
			t.Errorf("unexpected key: %s", param.Key)
			continue
		}

		switch param.Key {
		case "long_value":
			assert.Equal(t, expectedValue.(int), *param.LongV)
		case "double_value":
			assert.Equal(t, expectedValue.(float64), *param.DoubleV)
		case "bool_value":
			assert.Equal(t, expectedValue.(bool), *param.BoolV)
		case "str_value":
			assert.Equal(t, expectedValue.(string), *param.StrV)
		case "json_value":
			assert.Equal(t, expectedValue.(map[string]interface{}), param.JsonV)
		}
	}
}

func TestConvertDeviceAttributeMsgToBatchParams_InvalidDataType(t *testing.T) {
	msg := deviceAttributeMsg{
		DeviceId:  uuid.New().String(),
		TimeStamp: time.Now(),
		Data: map[string]interface{}{
			"unsupported_value": complex(1, 2),
		},
	}

	params, err := convertDeviceAttributeMsgToBatchParams(msg)

	assert.Error(t, err)
	assert.Nil(t, params)
}

func TestConvertDeviceAttributeMsgToBatchParams_InvalidDeviceID(t *testing.T) {
	msg := deviceAttributeMsg{
		DeviceId:  "invalid-uuid",
		TimeStamp: time.Now(),
		Data:      map[string]interface{}{},
	}

	params, err := convertDeviceAttributeMsgToBatchParams(msg)

	assert.Error(t, err)
	assert.Nil(t, params)
}

func TestDeviceAttributeProcessor_Start(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockStore := mockdb.NewStore(t)
	cfg := defaultDeviceAttributeProcessorConfig()
	payloadQueue := make(chan []byte)
	processor := NewDeviceAttributeProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	mockStore.On("BatchUpsertDeviceAttribute", mock.Anything, mock.Anything).Return(nil).Once()

	processor.Start(ctx, cfg, mockStore)

	// Simulate sending payload to processor
	payload := deviceAttributeMsg{
		DeviceId:  uuid.New().String(),
		TimeStamp: time.Now(),
		Data: map[string]interface{}{
			"attr1": 22.5,
			"attr2": true,
		},
	}
	payloadBytes, _ := json.Marshal(payload)
	payloadQueue <- payloadBytes

	time.Sleep(time.Millisecond * 20)

	cancel()

	mockStore.AssertExpectations(t)
}

func TestDeviceAttributeProcessor_ConvertWorker_InvalidJSON(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	payloadQueue := make(chan []byte)
	processor := NewDeviceAttributeProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go processor.convertWorker(ctx)

	payloadQueue <- []byte("invalid json")

	time.Sleep(time.Millisecond * 50)

	cancel()

	// No panic should occur
}

func TestDeviceAttributeProcessor_ConvertWorker_InvalidDeviceAttributeMsg(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	payloadQueue := make(chan []byte)
	processor := NewDeviceAttributeProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go processor.convertWorker(ctx)

	payloadQueue <- []byte(`{"device_id": "invalid-uuid"}`)

	time.Sleep(time.Millisecond * 50)

	cancel()

	// No panic should occur
}

func TestDeviceAttributeProcessor_ConvertWorker_QuitChannel(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	payloadQueue := make(chan []byte)
	processor := NewDeviceAttributeProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go processor.convertWorker(ctx)

	processor.quitCh <- true

	// No panic should occur
}

func TestDeviceAttributeProcessor_BatchUpsertWorker(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockStore := mockdb.NewStore(t)
	cfg := defaultDeviceAttributeProcessorConfig()
	payloadQueue := make(chan []byte)
	processor := NewDeviceAttributeProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	mockStore.On("BatchUpsertDeviceAttribute", mock.Anything, mock.Anything).Return(nil).Once()

	go processor.batchUpsertWorker(ctx, cfg, mockStore)

	param := repository.BatchUpsertDeviceAttributeParams{
		DeviceID:   uuid.New(),
		LastUpdate: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		Key:        "attr1",
		Scope:      repository.ClientScope,
		DoubleV:    new(float64),
	}

	processor.paramQueue <- param

	time.Sleep(time.Millisecond * 20)

	cancel()

	mockStore.AssertExpectations(t)
}

func TestDeviceAttributeProcessor_BatchUpsertWorker_QuitChannel(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockStore := mockdb.NewStore(t)
	cfg := defaultDeviceAttributeProcessorConfig()
	payloadQueue := make(chan []byte)
	processor := NewDeviceAttributeProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	mockStore.On("BatchUpsertDeviceAttribute", mock.Anything, mock.Anything).Return(nil).Once()

	go processor.batchUpsertWorker(ctx, cfg, mockStore)

	param := repository.BatchUpsertDeviceAttributeParams{
		DeviceID:   uuid.New(),
		LastUpdate: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		Key:        "attr1",
		Scope:      repository.ClientScope,
		DoubleV:    new(float64),
	}

	processor.paramQueue <- param

	time.Sleep(time.Millisecond * 20)

	processor.quitCh <- true

	mockStore.AssertExpectations(t)
}

func TestProcessDeviceAttributeBatch_Error(t *testing.T) {
	// Create a buffer to capture logs
	var buf bytes.Buffer

	// Create an encoder that writes to our buffer
	encoder := zapcore.NewConsoleEncoder(zap.NewDevelopmentEncoderConfig())
	core := zapcore.NewCore(
		encoder,
		zapcore.AddSync(&buf),
		zapcore.DebugLevel,
	)
	logger := zap.New(core)

	mockStore := mockdb.NewStore(t)

	batch := []repository.BatchUpsertDeviceAttributeParams{
		{Key: "temperature", DoubleV: new(float64)},
	}
	*batch[0].DoubleV = 22.5

	mockStore.On("BatchUpsertDeviceAttribute", mock.Anything, batch).Return(assert.AnError).Once()

	processDeviceAttributeBatch(context.Background(), mockStore, batch, logger)

	// Assert that the log message is as expected
	logOutput := buf.String()
	assert.Contains(t, logOutput, "failed to batch upsert device attribute")
	assert.Contains(t, logOutput, "assert.AnError")

	mockStore.AssertExpectations(t)
}
