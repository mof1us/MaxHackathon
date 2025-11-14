package domain

type User struct {
	ID        uint       `gorm:"primaryKey;autoIncrement:false" json:"id"`
	Schedules []Schedule `gorm:"many2many:user_schedules;" json:"schedules"`
}
