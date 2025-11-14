package postgres

import (
	"MAX-schedule/internal/domain"

	"gorm.io/gorm"
)

type TokensRepo struct {
	db *gorm.DB
}

func NewTokensRepo(db *gorm.DB) *TokensRepo {
	return &TokensRepo{db: db}
}

func (r *TokensRepo) GetByID(token string) (*domain.Token, error) {
	var t domain.Token
	if err := r.db.First(&t, "id = ?", token).Error; err != nil {
		return nil, err
	}
	return &t, nil
}

func (r *TokensRepo) Create(t *domain.Token) error {
	return r.db.Create(t).Error
}
