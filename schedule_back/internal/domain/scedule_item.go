package domain

import "time"

type ScheduleItem struct {
	ID          uint       `gorm:"primaryKey" json:"id"`
	Name        string     `gorm:"type:text;not null" json:"name"`
	Description string     `gorm:"type:text" json:"description"`
	Location    string     `gorm:"type:text" json:"location"`
	StartTime   *time.Time `gorm:"type:timestamp;not null" json:"start_time"`
	EndTime     *time.Time `gorm:"type:timestamp;not null" json:"end_time"`
	ScheduleID  uint       `gorm:"index" json:"schedule_id"`
}
