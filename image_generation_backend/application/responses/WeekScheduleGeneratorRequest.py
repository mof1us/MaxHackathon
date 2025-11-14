from pydantic import BaseModel

from application.responses.DayScheduleGenerationRequest import DayScheduleGenerationRequest


class WeekScheduleGeneratorRequest(BaseModel):
    name: str
    days: list[DayScheduleGenerationRequest]
