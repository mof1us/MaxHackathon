package migrations

import (
	"MAX-schedule/internal/domain"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)


func InitDB(dsn string) *gorm.DB {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect database: %v", err)
	}

	if err := db.AutoMigrate(&domain.Schedule{}, &domain.ScheduleItem{}, &domain.User{}); err != nil {
		log.Fatalf("migration failed: %v", err)
	}

	return db
}
