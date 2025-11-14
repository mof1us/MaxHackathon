package https

import (
	"log/slog"

	"github.com/gin-gonic/gin"
)

func NewRouter(h *ScheduleHandler, _ *slog.Logger) *gin.Engine {
	r := gin.Default()

	api := r.Group("/api")
	{
		schedule := api.Group("/schedule")
		{
			schedule.GET("/resolve_list", h.ResolveList) // 🔹 список кандидатов
			schedule.POST("/", h.Import)
			schedule.GET("/:id", h.GetByID)
			schedule.POST("/attach", h.AttachUser)
		}
		time := api.Group("/time")
		{
			time.GET("/day/:id", h.ScheduleForDay)
			time.GET("/week/:id", h.ScheduleForWeek)
			time.GET("/month/:id", h.ScheduleForMonth)
			time.GET("/all/:id", h.GetAllDateScheduleItems)
		}
		// <— новый эндпоинт
		api.POST("/token", h.GetOrGenerateToken)
	}

	api.GET("/users/:id/schedules", h.ListForUser)
	api.GET("/schedules/search", h.Search)

	return r
}
