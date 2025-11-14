package postgres

import (
	"MAX-schedule/internal/domain"

	"gorm.io/gorm"
)

type ScheduleRepo struct{ db *gorm.DB }

func NewScheduleRepo(db *gorm.DB) *ScheduleRepo { return &ScheduleRepo{db: db} }

func (r *ScheduleRepo) Create(s *domain.Schedule) error {
	return r.db.Create(s).Error
}

func (r *ScheduleRepo) GetByID(id uint) (domain.Schedule, error) {
	var s domain.Schedule
	err := r.db.Preload("Items").First(&s, id).Error
	return s, err
}

func (r *ScheduleRepo) SearchInUniversity(universityID uint, query string) ([]domain.Schedule, error) {
	var res []domain.Schedule
	q := r.db.Where("university_id = ?", universityID)
	if query != "" {
		q = q.Where("name ILIKE ?", "%"+query+"%")
	}
	err := q.Find(&res).Error
	return res, err
}

func (r *ScheduleRepo) ListByUserID(userID uint) ([]domain.Schedule, error) {
	var u domain.User
	if err := r.db.Preload("Schedules").First(&u, userID).Error; err != nil {
		return nil, err
	}
	return u.Schedules, nil
}
