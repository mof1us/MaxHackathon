package domain

type Schedule struct {
	ID           uint           `gorm:"primarykey" json:"id"`
	Name         string         `gorm:"type:text;not null" json:"name"`
	UniversityID uint           `gorm:"index" json:"university_id"`
	Items        []ScheduleItem `gorm:"foreignKey:ScheduleID;constraint:OnDelete:CASCADE" json:"items"`
}
