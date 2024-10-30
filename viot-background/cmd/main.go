package main

import (
	"context"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/jackc/pgx/v5/pgxpool"
	"go.uber.org/zap"

	"github.com/vuxmai/viot/viot-background/db/repository"
	"github.com/vuxmai/viot/viot-background/internal/processor"
	"github.com/vuxmai/viot/viot-background/pkg/config"
	"github.com/vuxmai/viot/viot-background/pkg/logger"
)

const (
	DeviceDataMqttTopic      = "v2/private/device_data"
	DeviceAttributeMqttTopic = "v2/private/device_attribute"
)

func NewMqttClient(cfg *config.MqttConfig, logger *zap.Logger) mqtt.Client {
	opts := mqtt.NewClientOptions()
	opts.AddBroker(cfg.BrokerUrl)
	opts.SetClientID(cfg.ClientId)
	opts.SetUsername(cfg.Username)
	opts.SetPassword(cfg.Password)
	opts.SetKeepAlive(time.Second * 60)

	opts.OnConnect = func(client mqtt.Client) {
		logger.Info("Connected to MQTT Broker")
	}
	opts.OnConnectionLost = func(client mqtt.Client, err error) {
		logger.Error("Connection lost: %v", zap.Error(err))
	}

	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		logger.Fatal("Failed to connect to MQTT Broker", zap.Error(token.Error()))
	}

	return client
}

func main() {
	// Load the configuration
	cfg := config.LoadConfig()

	logger := logger.NewZapLogger(cfg.Environment)

	// Context
	ctx := context.Background()

	// Database
	db, err := pgxpool.New(ctx, cfg.PostgresDsn)
	if err != nil {
		logger.Fatal(err.Error())
	}

	// Repository
	store := repository.NewStore(db)

	// Channel
	deviceDataCh := make(chan []byte, 10000)
	deviceAttributeCh := make(chan []byte, 10000)

	// Worker
	deviceDataProcessor := processor.NewDeviceDataProcessor(deviceDataCh, logger)
	deviceAttributeProcessor := processor.NewDeviceAttributeProcessor(deviceAttributeCh, logger)

	deviceDataProcessor.Start(ctx, &cfg.DeviceDataProcessorConfig, store)
	deviceAttributeProcessor.Start(ctx, &cfg.DeviceAttributeProcessorConfig, store)

	// MQTT Client
	client := NewMqttClient(&cfg.MqttConfig, logger)

	// Subscribe to topic
	token := client.Subscribe(DeviceDataMqttTopic, 2, func(_ mqtt.Client, msg mqtt.Message) {
		deviceDataCh <- msg.Payload()
	})
	if token.Wait() && token.Error() != nil {
		logger.Info("Subscribe error",
			zap.Error(token.Error()),
			zap.String("topic", DeviceDataMqttTopic))
	}

	token = client.Subscribe(DeviceAttributeMqttTopic, 2, func(_ mqtt.Client, msg mqtt.Message) {
		deviceAttributeCh <- msg.Payload()
	})
	if token.Wait() && token.Error() != nil {
		logger.Info("Subscribe error",
			zap.Error(token.Error()),
			zap.String("topic", DeviceAttributeMqttTopic))
	}

	select {}
}
