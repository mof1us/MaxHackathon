package main

import (
	"MAX-schedule/internal/config"
	"MAX-schedule/internal/inits/db"
	"MAX-schedule/internal/lib/logger/handlers/slogpretty"
	"MAX-schedule/internal/repo/postgres"
	"MAX-schedule/internal/service"
	"MAX-schedule/internal/transport/https"
	"fmt"
	"log/slog"
	"os"
)

func main() {
	cfg := config.MustLoad()
	logger := setUpLogger(cfg.Env)

	db.ConnectToDB(*cfg, logger)
	db.Migration(logger)

	scheduleRepo := postgres.NewScheduleRepo(db.DB)
	itemRepo := postgres.NewScheduleItemRepo(db.DB)
	userRepo := postgres.NewUserRepo(db.DB)
	tokenRepo := postgres.NewTokensRepo(db.DB) // <— новое

	scheduleService := service.NewScheduleService(scheduleRepo, itemRepo, userRepo, tokenRepo, logger)

	handler := https.NewScheduleHandler(scheduleService, logger)
	router := https.NewRouter(handler, logger)

	if err := router.Run(fmt.Sprintf("%s:%s", cfg.HTTPS.Host, cfg.HTTPS.Port)); err != nil {
		logger.Error("failed to start http server", slog.String("err", err.Error()))
	}
}

func setUpLogger(env string) *slog.Logger {
	return setupPrettySlog()
}
func setupPrettySlog() *slog.Logger {
	opts := slogpretty.PrettyHandlerOptions{
		SlogOpts: &slog.HandlerOptions{Level: slog.LevelDebug},
	}
	handler := opts.NewPrettyHandler(os.Stdout)
	return slog.New(handler)
}
