package postgres

import (
	"MAX-schedule/internal/domain"

	"gorm.io/gorm"
)

type UserRepo struct{ db *gorm.DB }

func NewUserRepo(db *gorm.DB) *UserRepo { return &UserRepo{db: db} }

func (r *UserRepo) FindByID(id uint) (*domain.User, error) {
	var u domain.User
	err := r.db.First(&u, id).Error
	return &u, err
}

func (r *UserRepo) CreateIfNotExists(id uint) (*domain.User, error) {
	u := domain.User{ID: id}
	err := r.db.FirstOrCreate(&u, domain.User{ID: id}).Error
	return &u, err
}

func (r *UserRepo) AttachSchedule(userID, scheduleID uint) error {
	u := domain.User{ID: userID}
	if err := r.db.FirstOrCreate(&u, domain.User{ID: userID}).Error; err != nil {
		return err
	}
	var s domain.Schedule
	if err := r.db.First(&s, scheduleID).Error; err != nil {
		return err
	}
	return r.db.Model(&u).Association("Schedules").Append(&s)
}

func (r *UserRepo) ListSchedules(userID uint) ([]domain.Schedule, error) {
	var u domain.User
	if err := r.db.Preload("Schedules").First(&u, userID).Error; err != nil {
		return nil, err
	}
	return u.Schedules, nil
}
