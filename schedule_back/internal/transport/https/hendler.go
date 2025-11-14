package https

import (
	"MAX-schedule/internal/service"
	"net/http"
	"strconv"
	"time"

	"log/slog"

	"github.com/gin-gonic/gin"
)

type ScheduleHandler struct {
	svc    service.ScheduleService
	logger *slog.Logger
}

func NewScheduleHandler(svc service.ScheduleService, logger *slog.Logger) *ScheduleHandler {
	return &ScheduleHandler{svc: svc, logger: logger}
}

// POST /api/token
// { "schedule_id": 11, "week_start": "2025-11-10T00:00:00Z" }  // RFC3339 или "YYYY-MM-DD"
// flag - day/week
func (h *ScheduleHandler) GetOrGenerateToken(c *gin.Context) {
	type req struct {
		ScheduleID uint   `json:"schedule_id" binding:"required"`
		WeekStart  string `json:"week_start"  binding:"required"`
		Flag       string `json:"flag" binding:"required"`
	}
	var r req
	if err := c.ShouldBindJSON(&r); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// допускаем 2 формата даты
	var ts time.Time
	var err error
	if ts, err = time.Parse(time.RFC3339, r.WeekStart); err != nil {
		ts, err = time.Parse("2006-01-02", r.WeekStart)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "week_start должен быть в RFC3339 или YYYY-MM-DD"})
			return
		}
	}

	token, err := h.svc.GetOrGenerateToken(r.ScheduleID, ts, r.Flag)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"id": token.ID, "token": token.Token})
}

func (h *ScheduleHandler) GetAllDateScheduleItems(c *gin.Context) {
	strid := c.Param("id")
	id, err := strconv.ParseUint(strid, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
	}
	var res []time.Time
	res, err = h.svc.GetAllDateSchedualeItems(uint(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	c.JSON(http.StatusOK, res)
}

// POST /api/schedule
// Форм‑поля: file(.ics) [обязательно], schedule_name [опц.], university_id [опц.]

func (h *ScheduleHandler) Import(c *gin.Context) {
	type ImportRequest struct {
		Link         string `json:"link" binding:"required"`
		ScheduleName string `json:"schedule_name" binding:"required"`
		UniversityID uint   `json:"university_id" binding:"required"`
		UserID       uint   `json:"user_id" binding:"required"`
	}

	var req ImportRequest

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	_, err := h.svc.ImportICS(req.Link, req.ScheduleName, req.UniversityID, req.UserID)
	if err != nil {
		h.logger.Error("import ics failed", slog.String("err", err.Error()))
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.Status(http.StatusCreated)
}

// GET /api/schedule/:id
func (h *ScheduleHandler) GetByID(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id должен быть числом"})
		return
	}
	sched, err := h.svc.GetScheduleByID(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, sched)
}

// POST /api/schedule/attach  {"schedule_id":1,"user_id":42}
type attachRequest struct {
	ScheduleID uint `json:"schedule_id" binding:"required"`
	UserID     uint `json:"user_id" binding:"required"`
}

func (h *ScheduleHandler) AttachUser(c *gin.Context) {
	var req attachRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "ожидался JSON: {schedule_id, user_id}"})
		return
	}
	if err := h.svc.AttachUserToSchedule(req.ScheduleID, req.UserID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.Status(http.StatusNoContent)
}

// GET /api/users/:id/schedules
func (h *ScheduleHandler) ListForUser(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "id должен быть числом"})
		return
	}
	list, err := h.svc.ListSchedulesForUser(uint(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, list)
}

// расписание на день
func (h *ScheduleHandler) ScheduleForDay(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	items, err := h.svc.ScheduleforDay(uint(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	c.JSON(http.StatusOK, items)
}

func (h *ScheduleHandler) ScheduleForWeek(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	items, err := h.svc.ScheduleforWeek(uint(id))

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	c.JSON(http.StatusOK, items)
}

func (h *ScheduleHandler) ScheduleForMonth(c *gin.Context) {
	idStr := c.Param("id")
	id, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	items, err := h.svc.ScheduleforMonth(uint(id))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
	c.JSON(http.StatusOK, items)
}

// GET /api/schedules/search?university_id=1&q=физика
func (h *ScheduleHandler) Search(c *gin.Context) {
	u := c.Query("id")
	if u == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "university_id обязателен"})
		return
	}
	uid, err := strconv.ParseUint(u, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "university_id должен быть числом"})
		return
	}
	q := c.Query("name")

	res, err := h.svc.SearchInUniversity(uint(uid), q)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, res)
}
