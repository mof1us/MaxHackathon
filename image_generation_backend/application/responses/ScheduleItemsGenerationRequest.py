from pydantic import BaseModel


class ScheduleItemsGenerationRequest(BaseModel):
    name: str
    description: str
    location: str
    start_time: str
    end_time: str