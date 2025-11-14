package parser

import (
	"MAX-schedule/internal/domain"
	"io"

	"github.com/apognu/gocal"
)

func ParseICSReader(file io.Reader) ([]domain.ScheduleItem, error) {
	c := gocal.NewParser(file)
	c.SkipBounds = true
	if err := c.Parse(); err != nil {
		return nil, err
	}
	var events []domain.ScheduleItem
	for _, ev := range c.Events {
		events = append(events, domain.ScheduleItem{
			Name:        ev.Summary,
			Description: ev.Description,
			Location:    ev.Location,
			StartTime:   ev.Start,
			EndTime:     ev.End,
		})
	}
	return events, nil
}
