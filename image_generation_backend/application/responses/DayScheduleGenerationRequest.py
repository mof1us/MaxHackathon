from pydantic import BaseModel

from application.responses.ScheduleItemsGenerationRequest import ScheduleItemsGenerationRequest


class DayScheduleGenerationRequest(BaseModel):
    weekday: str
    item_list: list[ScheduleItemsGenerationRequest]