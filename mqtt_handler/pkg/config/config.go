package config

import (
	"log"

	"github.com/caarlos0/env/v6"
	_ "github.com/joho/godotenv/autoload"
)

// Logger constants
const (
	ProdEnvVal = "production"
)

type Config struct {
	Environment string `env:"ENVIRONMENT" envDefault:"development"`
	PostgresDsn string `env:"POSTGRES_DSN"`
	MqttConfig  MqttConfig

	DeviceDataProcessorConfig DeviceDataProcessorConfig
}

type MqttConfig struct {
	BrokerUrl string `env:"MQTT_BROKER_URL"`
	ClientId  string `env:"MQTT_CLIENT_ID"`
	Username  string `env:"MQTT_USERNAME"`
	Password  string `env:"MQTT_PASSWORD"`
}

type DeviceDataProcessorConfig struct {
	MaxBatchSize       int `env:"MAX_BATCH_SIZE" envDefault:"500"`
	MaxBatchIntervalMs int `env:"MAX_BATCH_INTERVAL_SEC" envDefault:"2000"`
}

func LoadConfig() *Config {
	cfg := &Config{}
	if err := env.Parse(cfg); err != nil {
		log.Fatalf("Failed to parse config: %v", err)
		return nil
	}

	return cfg
}
