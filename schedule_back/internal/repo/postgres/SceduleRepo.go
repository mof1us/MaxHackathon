package postgres

import (
	"MAX-schedule/internal/domain"
	"strings"

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

/* ===== Новое: один лучший кандидат (для совместимости с существующим сервисом) ===== */
func (r *ScheduleRepo) ResolveApprox(universityID uint, q string) (domain.Schedule, error) {
	var out domain.Schedule

	const sqlTrgm = `
		SELECT id, name
		FROM schedules
		WHERE university_id = ?
		  AND (
		       CAST(? AS text) = ''
		    OR name % CAST(? AS text)
		    OR name ILIKE ('%' || CAST(? AS text) || '%')
		    OR name ILIKE (CAST(? AS text) || '%')
		  )
		ORDER BY similarity(name, CAST(? AS text)) DESC, name ASC
		LIMIT 1;
	`

	err := r.db.Raw(sqlTrgm, universityID, q, q, q, q, q).Scan(&out).Error
	if err != nil && (strings.Contains(err.Error(), "42883") ||
		strings.Contains(err.Error(), "operator does not exist") ||
		strings.Contains(err.Error(), "function similarity") ||
		strings.Contains(err.Error(), "pg_trgm")) {

		const sqlFallback = `
			SELECT id, name
			FROM schedules
			WHERE university_id = ?
			  AND (
			       CAST(? AS text) = ''
			    OR name ILIKE ('%' || CAST(? AS text) || '%')
			    OR name ILIKE (CAST(? AS text) || '%')
			  )
			ORDER BY name ASC
			LIMIT 1;
		`
		err = r.db.Raw(sqlFallback, universityID, q, q, q).Scan(&out).Error
	}
	if err != nil {
		return out, err
	}
	if out.ID == 0 {
		return out, gorm.ErrRecordNotFound
	}
	return out, nil
}

/* ===== Новое: много результатов (топ‑N) ===== */
func (r *ScheduleRepo) ResolveApproxList(universityID uint, q string, limit int, minScore float64) ([]domain.Schedule, error) {
	if limit <= 0 || limit > 50 {
		limit = 10
	}
	var rows []domain.Schedule

	const sqlTrgm = `
		SELECT id, name
		FROM schedules
		WHERE university_id = ?
		  AND (
		       CAST(? AS text) = ''
		    OR name % CAST(? AS text)
		    OR name ILIKE ('%' || CAST(? AS text) || '%')
		    OR name ILIKE (CAST(? AS text) || '%')
		  )
		  AND (
		       CAST(? AS text) = ''
		    OR similarity(name, CAST(? AS text)) >= ?
		  )
		ORDER BY similarity(name, CAST(? AS text)) DESC, name ASC
		LIMIT ?;
	`
	err := r.db.Raw(sqlTrgm,
		universityID,
		q, q, q, q, // фильтр по запросу
		q, q, minScore,
		q, // order by similarity(name, q)
		limit,
	).Scan(&rows).Error

	if err != nil && (strings.Contains(err.Error(), "42883") ||
		strings.Contains(err.Error(), "operator does not exist") ||
		strings.Contains(err.Error(), "function similarity") ||
		strings.Contains(err.Error(), "pg_trgm")) {

		const sqlFallback = `
			SELECT id, name
			FROM schedules
			WHERE university_id = ?
			  AND (
			       CAST(? AS text) = ''
			    OR name ILIKE ('%' || CAST(? AS text) || '%')
			    OR name ILIKE (CAST(? AS text) || '%')
			  )
			ORDER BY
				CASE WHEN name ILIKE (CAST(? AS text) || '%') THEN 0 ELSE 1 END,
				POSITION(LOWER(CAST(? AS text)) IN LOWER(name)),
				LENGTH(name), name
			LIMIT ?;
		`
		rows = nil
		err = r.db.Raw(sqlFallback, universityID, q, q, q, q, limit).Scan(&rows).Error
	}

	return rows, err
}
