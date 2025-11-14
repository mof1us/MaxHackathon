package db

import (
	"MAX-schedule/internal/config"
	"MAX-schedule/internal/domain"
	"fmt"
	"log"
	"log/slog"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func ConnectToDB(cfg config.Config, logger *slog.Logger) {
	dsn := "host=" + cfg.DB.Host + " user=" + cfg.DB.User + " password=" + cfg.DB.Password + " dbname=" + cfg.DB.Name + " port=" + cfg.DB.Port + " sslmode=" + cfg.DB.SSLMode + " TimeZone=UTC"
	var err error

	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		logger.Debug("config.DB", slog.Any("DB_conf", cfg.DB))
		logger.Debug("Failed to connect to database!", slog.String("dsn", dsn), slog.String("error", err.Error()))
		panic("Failed to connect to database!")
	}
}

func Migration(logger *slog.Logger) {

	err := DB.AutoMigrate(&domain.Schedule{},
		&domain.User{},
		&domain.ScheduleItem{},
		&domain.Token{})
	if err != nil {
		logger.Debug("Migration failed!", slog.String("error", err.Error()))
		log.Fatal(fmt.Errorf("не удалось осуществить миграцию %w", err))
	}
}
