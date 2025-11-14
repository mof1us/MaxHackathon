package postgres

import (
	"MAX-schedule/internal/domain"
	"time"

	"gorm.io/gorm"
)

type ScheduleItemRepo struct{ db *gorm.DB }

func NewScheduleItemRepo(db *gorm.DB) *ScheduleItemRepo { return &ScheduleItemRepo{db: db} }

func (r *ScheduleItemRepo) CreateBatch(items []domain.ScheduleItem) error {
	if len(items) == 0 {
		return nil
	}
	return r.db.Create(&items).Error
}

func (r *ScheduleItemRepo) GetByDateRange(ScheduleID uint, startTime, endtime time.Time) ([]domain.ScheduleItem, error) {
	var items []domain.ScheduleItem
	err := r.db.Where("schedule_id = ? AND start_time BETWEEN ? and ?", ScheduleID, startTime, endtime).
		Order("start_time ASC").
		Find(&items).Error
	return items, err
}

func (r *ScheduleItemRepo) GetAllDate(scheduleID uint) ([]string, error) {
	var times []string
	now := time.Now()
	start := now.AddDate(-1, 0, 0)
	end := now.AddDate(1, 0, 0)
	err := r.db.
		Table("schedule_items").
		Select("DISTINCT DATE(start_time)").
		Where("schedule_id = ? AND start_time BETWEEN ? AND ?", scheduleID, start, end).
		Order("DATE(start_time) ASC").
		Scan(&times).Error
	return times, err
}
