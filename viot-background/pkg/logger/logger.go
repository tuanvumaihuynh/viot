package logger

import (
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"

	"github.com/vuxmai/viot/viot-background/pkg/config"
)

func NewZapLogger(environment string) *zap.Logger {
	var conf zap.Config
	conf = NewProductionConfig()

	if environment != config.ProdEnvVal {
		conf = zap.NewDevelopmentConfig()
	}

	conf.DisableStacktrace = true
	log, err := conf.Build()
	if err != nil {
		panic(err)
	}

	return log
}

func NewProductionConfig() zap.Config {
	return zap.Config{
		Level:       zap.NewAtomicLevelAt(zap.InfoLevel),
		Development: false,
		Sampling: &zap.SamplingConfig{
			Initial:    100,
			Thereafter: 100,
		},
		Encoding:         "console",
		EncoderConfig:    NewProductionEncoderConfig(),
		OutputPaths:      []string{"stderr"},
		ErrorOutputPaths: []string{"stderr"},
	}
}

func NewProductionEncoderConfig() zapcore.EncoderConfig {
	return zapcore.EncoderConfig{
		TimeKey:        "ts",
		LevelKey:       "level",
		NameKey:        "logger",
		CallerKey:      "caller",
		MessageKey:     "msg",
		StacktraceKey:  "stacktrace",
		LineEnding:     zapcore.DefaultLineEnding,
		EncodeLevel:    zapcore.CapitalLevelEncoder,
		EncodeTime:     zapcore.ISO8601TimeEncoder,
		EncodeDuration: zapcore.SecondsDurationEncoder,
		EncodeCaller:   zapcore.ShortCallerEncoder,
	}
}
