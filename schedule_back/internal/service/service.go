package service

import (
	"MAX-schedule/internal/domain"
	"MAX-schedule/internal/parser"
	"MAX-schedule/internal/repo/postgres"
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/jinzhu/now"
	"gorm.io/gorm"
)

type ScheduleService interface {
	ResolveSchedule(universityID uint, name string) (domain.Schedule, error)
	ResolveScheduleList(universityID uint, name string, limit int, minScore float64) ([]domain.Schedule, error)

	GetOrGenerateToken(scheduleID uint, weekStart time.Time, flag string) (domain.Token, error)

	ImportICS(fileLink string, schedule_name string, university_id uint, user_id uint) (*domain.Schedule, error)
	GetScheduleByID(id uint) (domain.Schedule, error)
	ListSchedulesForUser(userID uint) ([]domain.Schedule, error)
	AttachUserToSchedule(scheduleID, userID uint) error
	SearchInUniversity(universityID uint, q string) ([]domain.Schedule, error)

	// выборка расписания
	ScheduleforDay(idSchedule uint) (DayItemsGroup, error)
	ScheduleforWeek(idSchedule uint) (WeeksResponse, error)
	ScheduleforMonth(idSchedule uint) ([]domain.ScheduleItem, error)

	// только даты, на год назад и на год вперёд
	GetAllDateSchedualeItems(idSchedule uint) ([]time.Time, error)

	// произвольный диапазон
	GetByDateRange(scheduleID uint, start, end time.Time) ([]domain.ScheduleItem, error)
}

type scheduleService struct {
	schedules *postgres.ScheduleRepo
	items     *postgres.ScheduleItemRepo
	users     *postgres.UserRepo
	tokens    *postgres.TokensRepo
	logger    *slog.Logger
}

func NewScheduleService(
	s *postgres.ScheduleRepo,
	i *postgres.ScheduleItemRepo,
	u *postgres.UserRepo,
	t *postgres.TokensRepo,
	l *slog.Logger,
) ScheduleService {
	return &scheduleService{schedules: s, items: i, users: u, tokens: t, logger: l}
}

func (s *scheduleService) ResolveSchedule(universityID uint, name string) (domain.Schedule, error) {
	return s.schedules.ResolveApprox(universityID, strings.TrimSpace(name))
}

func (s *scheduleService) ResolveScheduleList(universityID uint, name string, limit int, minScore float64) ([]domain.Schedule, error) {
	return s.schedules.ResolveApproxList(universityID, strings.TrimSpace(name), limit, minScore)
}

//* TOKEN

// ---------- публичный метод ----------
func (s *scheduleService) GetOrGenerateToken(scheduleID uint, weekStart time.Time, flag string) (domain.Token, error) {
	start, end := boundsOfWeekUTC(weekStart)
	hash := weekHash(scheduleID, start, flag)
	// 1) проверяем БД
	if existing, err := s.tokens.GetByID(hash); err == nil {
		return *existing, nil
	} else if !errors.Is(err, gorm.ErrRecordNotFound) {
		return domain.Token{}, err
	}

	// 2) собираем данные за период
	items, err := s.items.GetByDateRange(scheduleID, start, end)
	if err != nil {
		return domain.Token{}, err
	}
	shedule, err := s.schedules.GetByID(scheduleID)
	if err != nil {
		return domain.Token{}, err
	}
	nameShedule := shedule.Name
	var name string
	var days []DayItemsGroup

	if flag == "week" {
		weekPayload := gropItemsByWeekDay(items, nameShedule)
		name = weekPayload.Name
		days = weekPayload.Days
		// 3) вызываем сервис генерации
		tokenStr, errr := s.callGenerationServiceWeek(scheduleID, weekStart, name, days, hash)
		if errr != nil {
			fmt.Println("error", errr)
			return domain.Token{}, errr
		}
		// 4) сохраняем и возвращаем
		t := domain.Token{ID: hash, Token: tokenStr}
		fmt.Println("токен недели")
		if err := s.tokens.Create(&t); err != nil {
			return domain.Token{}, err
		}
		return t, nil
	} else if flag == "day" {
		dayPayload := groupItemsByDay(items)
		tokenStr, errr := s.callGenerationServiceDay(dayPayload)
		if errr != nil {
			return domain.Token{}, errr
		}
		// 4) сохраняем и возвращаем
		t := domain.Token{ID: hash, Token: tokenStr}
		if err := s.tokens.Create(&t); err != nil {
			return domain.Token{}, err
		}
		return t, nil
	} else {
		return domain.Token{}, errors.New("invalid flag")
	}

}

// ---------- helpers ----------

// нормализуем в понедельник 00:00:00 UTC и берём конец недели
func boundsOfWeekUTC(ts time.Time) (time.Time, time.Time) {
	// Monday-first неделя
	wd := int(ts.Weekday())
	if wd == 0 { // Sunday -> 6
		wd = 7
	}
	// сдвиг к понедельнику
	monday := time.Date(ts.Year(), ts.Month(), ts.Day()-(wd-1), 0, 0, 0, 0, time.UTC)
	// конец недели — воскресенье 23:59:59 UTC
	end := monday.AddDate(0, 0, 7).Add(-time.Nanosecond)
	return monday, end
}

func weekHash(scheduleID uint, mondayUTC time.Time, flag string) string {
	key := fmt.Sprintf("%d:%s:%s", scheduleID, mondayUTC.Format("2006-01-02"), flag)
	sum := sha256.Sum256([]byte(key))
	return hex.EncodeToString(sum[:])
}

func (s *scheduleService) callGenerationServiceDay(DayGroup DayItemsGroup) (string, error) {
	fmt.Println("день")
	body, err := json.Marshal(DayGroup)
	if err != nil {
		return "", err
	}
	req, err := http.NewRequest(http.MethodPost, os.Getenv("defaultGenURLDay"), bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	defer req.Body.Close()
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	b, _ := io.ReadAll(resp.Body)
	fmt.Println(string(b))
	var out struct {
		Token string `json:"token"`
	}
	if err := json.Unmarshal(b, &out); err != nil || out.Token == "" {
		if err != nil {
			return "", err
		}
	}
	return out.Token, nil
}

// Отправляем POST данные недели. Если сервис недоступен — делаем "тихую" заглушку: tok_<hash>.
func (s *scheduleService) callGenerationServiceWeek(scheduleID uint, weekStart time.Time, name string, days []DayItemsGroup, hash string) (string, error) {
	fmt.Println("неделя")
	payload := struct {
		//ScheduleID uint            `json:"schedule_id"`
		//WeekStart  string          `json:"week_start"` // RFC3339 UTC
		Name string          `json:"name"`
		Days []DayItemsGroup `json:"days"`
	}{
		//ScheduleID: scheduleID,
		//WeekStart:  weekStart.UTC().Format(time.RFC3339),
		Name: name,
		Days: days,
	}
	body, _ := json.Marshal(payload)
	fmt.Println(string(body))
	req, _ := http.NewRequest(http.MethodPost, os.Getenv("defaultGenURLWeek"), bytes.NewBuffer(body))
	fmt.Println("я тут ")
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	fmt.Println(resp)
	fmt.Println(err)
	if err != nil {
		fmt.Println("ошибка")
		return "", err
	}
	defer resp.Body.Close()

	b, _ := io.ReadAll(resp.Body)
	fmt.Println(string(b))
	var out struct {
		Token string `json:"token"`
	}
	if err := json.Unmarshal(b, &out); err != nil || out.Token == "" {
		if err != nil {
			return "", err
		}
	}
	if out.Token == "" {
		return "", errors.New("пустой токен")
	}
	return out.Token, err
}
func (s *scheduleService) GetAllDateSchedualeItems(idSchedule uint) ([]time.Time, error) {
	nowTime := time.Now()
	start := nowTime.AddDate(-1, 0, 0)
	end := nowTime.AddDate(1, 0, 0)

	items, err := s.items.GetByDateRange(idSchedule, start, end)
	if err != nil {
		return nil, err
	}

	uniq := make(map[time.Time]struct{})
	for _, it := range items {
		if it.StartTime == nil {
			continue
		}
		t := *it.StartTime
		dateOnly := time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, t.Location())
		uniq[dateOnly] = struct{}{}
	}

	dates := make([]time.Time, 0, len(uniq))
	for d := range uniq {
		dates = append(dates, d)
	}

	// сортируем по возрастанию
	sort.Slice(dates, func(i, j int) bool {
		return dates[i].Before(dates[j])
	})

	return dates, nil
}

func (s *scheduleService) ScheduleforDay(idSchedule uint) (DayItemsGroup, error) {
	startOfDay := now.BeginningOfDay()
	endOfDay := now.EndOfDay()
	items, err := s.items.GetByDateRange(idSchedule, startOfDay, endOfDay)
	//schedule, err := s.schedules.GetByID(idSchedule)
	//scheduleName := schedule.Name
	res := groupItemsByDay(items)

	return res, err
}

func (s *scheduleService) ScheduleforWeek(idSchedule uint) (WeeksResponse, error) {
	startOfWeek := now.BeginningOfWeek()
	endOfWeek := now.EndOfWeek()
	items, err := s.items.GetByDateRange(idSchedule, startOfWeek, endOfWeek)
	schedule, err := s.schedules.GetByID(idSchedule)
	scheduleName := schedule.Name
	res := gropItemsByWeekDay(items, scheduleName)
	return res, err
}

func (s *scheduleService) ScheduleforMonth(idSchedule uint) ([]domain.ScheduleItem, error) {
	startOfMonth := now.BeginningOfMonth()
	endOfMonth := now.EndOfMonth()
	items, err := s.items.GetByDateRange(idSchedule, startOfMonth, endOfMonth)
	s.logger.Debug("items", items)
	s.logger.Debug("startOfMonth", startOfMonth)
	s.logger.Debug("endOfMonth", endOfMonth)
	return items, err
}

func (s *scheduleService) ImportICS(fileLink string, scheduleName string, universityID uint, user_id uint) (*domain.Schedule, error) {
	fileResp, err := http.Get(fileLink)
	if err != nil {
		return nil, err
	}
	_, params, err := mime.ParseMediaType(fileResp.Header.Get("Content-Disposition"))
	if err != nil {
		return nil, err
	}

	filename := params["filename"] // ← вот здесь у тебя строка
	fmt.Println(filename)
	body, err := io.ReadAll(fileResp.Body)
	if err != nil {
		return nil, err
	}
	rider := bytes.NewReader(body)
	var events []domain.ScheduleItem
	events, err = parser.ParseICSReader(rider)
	if err != nil {
		return &domain.Schedule{}, err
	}

	name := strings.TrimSpace(scheduleName)
	if name == "" {
		base := strings.TrimSuffix(filepath.Base(filename), filepath.Ext(filename))
		if base == "" {
			base = "Расписание"
		}
		name = fmt.Sprintf("%s (%s)", base, time.Now().Format("2006-01-02"))
	}

	schedule := domain.Schedule{
		Name:         name,
		UniversityID: universityID,
	}
	if err := s.schedules.Create(&schedule); err != nil {
		return &domain.Schedule{}, err
	}

	for i := range events {
		events[i].ScheduleID = schedule.ID
		if events[i].StartTime == nil {
			t := time.Now()
			events[i].StartTime = &t
		}
		if events[i].EndTime == nil {
			t := events[i].StartTime.Add(time.Hour)
			events[i].EndTime = &t
		}
	}

	if err := s.items.CreateBatch(events); err != nil {
		return &domain.Schedule{}, err
	}

	created, err := s.schedules.GetByID(schedule.ID)
	if err != nil {

		return &schedule, nil
	}
	err = s.AttachUserToSchedule(schedule.ID, user_id)
	if err != nil {
		return nil, err
	}
	err = fileResp.Body.Close()
	return &created, err
}

//func (s *scheduleService) ImportICS(file , filename string, universityID uint, scheduleName string) (domain.Schedule, error) {
//
//	events, err := parser.ParseICSReader(file)
//	if err != nil {
//		return domain.Schedule{}, err
//	}
//
//	name := strings.TrimSpace(scheduleName)
//	if name == "" {
//		base := strings.TrimSuffix(filepath.Base(filename), filepath.Ext(filename))
//		if base == "" {
//			base = "Расписание"
//		}
//		name = fmt.Sprintf("%s (%s)", base, time.Now().Format("2006-01-02"))
//	}
//
//	schedule := domain.Schedule{
//		Name:         name,
//		UniversityID: universityID,
//	}
//	if err := s.schedules.Create(&schedule); err != nil {
//		return domain.Schedule{}, err
//	}
//
//	for i := range events {
//		events[i].ScheduleID = schedule.ID
//		if events[i].StartTime == nil {
//			t := time.Now()
//			events[i].StartTime = &t
//		}
//		if events[i].EndTime == nil {
//			t := events[i].StartTime.Add(time.Hour)
//			events[i].EndTime = &t
//		}
//	}
//
//	if err := s.items.CreateBatch(events); err != nil {
//		return domain.Schedule{}, err
//	}
//
//	created, err := s.schedules.GetByID(schedule.ID)
//	if err != nil {
//
//		return schedule, nil
//	}
//	return created, nil
//}

func (s *scheduleService) GetScheduleByID(id uint) (domain.Schedule, error) {
	return s.schedules.GetByID(id)
}

func (s *scheduleService) ListSchedulesForUser(userID uint) ([]domain.Schedule, error) {
	return s.schedules.ListByUserID(userID)
}

func (s *scheduleService) AttachUserToSchedule(scheduleID, userID uint) error {
	return s.users.AttachSchedule(userID, scheduleID)
}

func (s *scheduleService) SearchInUniversity(universityID uint, q string) ([]domain.Schedule, error) {
	return s.schedules.SearchInUniversity(universityID, q)
}

func (s *scheduleService) GetByDateRange(scheduleID uint, start, end time.Time) ([]domain.ScheduleItem, error) {
	return s.items.GetByDateRange(scheduleID, start, end)
}

type DayItemsGroup struct {
	Weekday  string                `json:"weekday"`
	ItemList []domain.ScheduleItem `json:"item_list"`
}
type WeeksResponse struct {
	Name string          `json:"name"`
	Days []DayItemsGroup `json:"days"`
}
type DayResponse struct {
	Name string          `json:"name"`
	Days []DayItemsGroup `json:"days"`
}

// Функция группировки
func groupItemsByDay(items []domain.ScheduleItem) DayItemsGroup {
	result := DayItemsGroup{
		Weekday:  "",
		ItemList: []domain.ScheduleItem{},
	}

	if len(items) == 0 {
		return result
	}

	first := items[0]
	if first.StartTime != nil {
		result.Weekday = weekdayToRu(first.StartTime.Weekday())
	}

	for _, item := range items {
		if item.StartTime == nil {
			continue
		}

		if weekdayToRu(item.StartTime.Weekday()) == result.Weekday {
			result.ItemList = append(result.ItemList, item)
		}
	}

	return result
}

func weekdayToRu(w time.Weekday) string {
	switch w {
	case time.Monday:
		return "Понедельник"
	case time.Tuesday:
		return "Вторник"
	case time.Wednesday:
		return "Среда"
	case time.Thursday:
		return "Четверг"
	case time.Friday:
		return "Пятница"
	case time.Saturday:
		return "Суббота"
	case time.Sunday:
		return "Воскресенье"
	}
	return ""
}

func gropItemsByWeekDay(items []domain.ScheduleItem, scheduleName string) WeeksResponse {
	result := []DayItemsGroup{
		{Weekday: "Понедельник", ItemList: []domain.ScheduleItem{}},
		{Weekday: "Вторник", ItemList: []domain.ScheduleItem{}},
		{Weekday: "Среда", ItemList: []domain.ScheduleItem{}},
		{Weekday: "Четверг", ItemList: []domain.ScheduleItem{}},
		{Weekday: "Пятница", ItemList: []domain.ScheduleItem{}},
		{Weekday: "Суббота", ItemList: []domain.ScheduleItem{}},
	}

	for _, item := range items {
		if item.StartTime == nil {
			continue
		}

		weekday := item.StartTime.Weekday()

		if weekday == time.Sunday {
			continue
		}

		index := int(weekday) - 1

		if index < 0 || index >= len(result) {
			continue
		}

		result[index].ItemList = append(result[index].ItemList, item)
	}

	return WeeksResponse{
		Name: scheduleName,
		Days: result,
	}
}
