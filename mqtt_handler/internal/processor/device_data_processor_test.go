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

	mockdb "github.com/vuxmai/viot/mqtt_handler/db/mock"
	"github.com/vuxmai/viot/mqtt_handler/db/repository"
	"github.com/vuxmai/viot/mqtt_handler/pkg/config"
)

const (
	DeviceDataMaxBatchSize       = 2
	DeviceDataMaxBatchIntervalMs = 10
	TestDeviceDataKey            = "temperature"
	TestDoubleValue              = 22.5
)

// Creates a new DeviceDataProcessorConfig with default values
func defaultDeviceDataProcessorConfig() *config.DeviceDataProcessorConfig {
	return &config.DeviceDataProcessorConfig{
		MaxBatchSize:       DeviceDataMaxBatchSize,
		MaxBatchIntervalMs: DeviceDataMaxBatchIntervalMs,
	}
}

// Creates a new BatchInsertDeviceDataParams with default values
func newTestBatchInsertParam() repository.BatchInsertDeviceDataParams {
	param := repository.BatchInsertDeviceDataParams{
		DeviceID: uuid.New(),
		Ts:       pgtype.Timestamptz{Time: time.Now(), Valid: true},
		Key:      TestDeviceDataKey,
		DoubleV:  new(float64),
	}
	*param.DoubleV = TestDoubleValue
	return param
}

func TestConvertDeviceDataMsgToBatchParams(t *testing.T) {
	data := map[string]interface{}{
		"long_value":   100000000000000000,
		"double_value": 22.5,
		"bool_value":   true,
		"str_value":    "sensor1",
		"json_value": map[string]interface{}{
			"key1": "value1",
			"key2": "value2",
		},
	}

	msg := deviceDataMsg{
		DeviceId:  uuid.New().String(),
		TimeStamp: time.Now(),
		Data:      data,
	}

	batchParams, err := convertDeviceDataMsgToBatchParams(msg)

	assert.NoError(t, err)
	assert.Len(t, batchParams, 5)

	for _, param := range batchParams {
		expectedValue, exists := data[param.Key]
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

func TestConvertDeviceDataMsgToBatchParams_InvalidDataType(t *testing.T) {
	msg := deviceDataMsg{
		DeviceId:  uuid.New().String(),
		TimeStamp: time.Now(),
		Data: map[string]interface{}{
			"unsupported_value": complex(1, 2),
		},
	}

	batchParams, err := convertDeviceDataMsgToBatchParams(msg)

	assert.Error(t, err)
	assert.Nil(t, batchParams)
	assert.Equal(t, "unsupported data type: complex128", err.Error())
}

func TestConvertDeviceDataMsgToBatchParams_InvalidDeviceID(t *testing.T) {
	msg := deviceDataMsg{
		DeviceId:  "invalid-uuid",
		TimeStamp: time.Now(),
		Data: map[string]interface{}{
			"temperature": 22.5,
			"status":      true,
			"device_name": "sensor1",
		},
	}

	_, err := convertDeviceDataMsgToBatchParams(msg)

	assert.Error(t, err)
}

func TestDeviceDataProcessor_Start(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockStore := mockdb.NewStore(t)
	cfg := defaultDeviceDataProcessorConfig()
	payloadQueue := make(chan []byte)
	processor := NewDeviceDataProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	mockStore.On("BatchInsertDeviceData", mock.Anything, mock.Anything).Return(nil).Once()

	processor.Start(ctx, cfg, mockStore)

	// Simulate sending payload to processor
	payload := deviceDataMsg{
		DeviceId:  uuid.New().String(),
		TimeStamp: time.Now(),
		Data: map[string]interface{}{
			"temperature": 22.5,
			"status":      true,
		},
	}
	payloadBytes, _ := json.Marshal(payload)
	payloadQueue <- payloadBytes

	time.Sleep(time.Millisecond * 20)

	cancel()

	mockStore.AssertExpectations(t)
}

func TestDeviceDataProcessor_ConvertWorker_InvalidJSON(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	payloadQueue := make(chan []byte)
	processor := NewDeviceDataProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go processor.convertWorker(ctx)

	payloadQueue <- []byte("invalid json")

	time.Sleep(time.Millisecond * 50)

	cancel()

	// No panic should occur
}

func TestDeviceDataProcessor_ConvertWorker_InvalidDeviceDataMsg(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	payloadQueue := make(chan []byte)
	processor := NewDeviceDataProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go processor.convertWorker(ctx)

	payloadQueue <- []byte(`{"device_id": "invalid-uuid"}`)

	time.Sleep(time.Millisecond * 50)

	cancel()

	// No panic should occur
}

func TestDeviceDataProcessor_ConvertWorker_QuitChannel(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	payloadQueue := make(chan []byte)
	processor := NewDeviceDataProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go processor.convertWorker(ctx)

	processor.quitCh <- true

	// No panic should occur
}

func TestDeviceDataProcessor_BatchInsertWorker(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockStore := mockdb.NewStore(t)
	cfg := defaultDeviceDataProcessorConfig()
	payloadQueue := make(chan []byte)
	processor := NewDeviceDataProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	mockStore.On("BatchInsertDeviceData", mock.Anything, mock.Anything).Return(nil).Once()

	go processor.batchInsertWorker(ctx, cfg, mockStore)

	param := newTestBatchInsertParam()

	processor.paramQueue <- param

	time.Sleep(time.Millisecond * 20)

	cancel()

	mockStore.AssertExpectations(t)
}

func TestDeviceDataProcessor_BatchInsertWorker_QuitChannel(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockStore := mockdb.NewStore(t)
	cfg := &config.DeviceDataProcessorConfig{MaxBatchSize: 2, MaxBatchIntervalMs: 10}
	payloadQueue := make(chan []byte)
	processor := NewDeviceDataProcessor(payloadQueue, logger)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	mockStore.On("BatchInsertDeviceData", mock.Anything, mock.Anything).Return(nil).Once()

	go processor.batchInsertWorker(ctx, cfg, mockStore)

	param := newTestBatchInsertParam()

	processor.paramQueue <- param

	time.Sleep(time.Millisecond * 20)

	processor.quitCh <- true

	mockStore.AssertExpectations(t)
}

func TestProcessBatch_Error(t *testing.T) {
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

	batch := []repository.BatchInsertDeviceDataParams{
		{Key: "temperature", DoubleV: new(float64)},
	}
	*batch[0].DoubleV = 22.5

	mockStore.On("BatchInsertDeviceData", mock.Anything, batch).Return(assert.AnError).Once()

	processBatch(context.Background(), mockStore, batch, logger)

	// Assert that the log message is as expected
	logOutput := buf.String()
	assert.Contains(t, logOutput, "Error inserting batch")
	assert.Contains(t, logOutput, "assert.AnError")

	mockStore.AssertExpectations(t)
}
