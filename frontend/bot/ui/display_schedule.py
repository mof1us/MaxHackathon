from datetime import datetime, date
import random
from typing import Literal
from bot.api.schedule_api import get_schedule_token
from bot.menus.schedule.schedule_display.schedule_display import schedule_day_display, schedule_display, schedule_week_select
from maxapi.types.attachments.attachment import Attachment

async def display_schedule(curr_date: str, schedule_id: int, flag: Literal["week", "day"], is_schedule_added: bool = False, available_days: list[date] = [], ) -> tuple[str, list[Attachment]]:
    picture_token = await get_schedule_token(schedule_id, datetime.fromisoformat(curr_date), flag=flag)

    keyboard = schedule_day_display(
            schedule_id=int(schedule_id),
            current_date=datetime.fromisoformat(curr_date),
            available_days=available_days,
            is_schedule_added=is_schedule_added
        ) if flag == "day" else schedule_display(
            schedule_id=schedule_id,
            current_date=datetime.fromisoformat(curr_date),
            available_days=available_days,
            is_schedule_added=is_schedule_added
        )

    answer_payloads = [keyboard,{
            "type": "image",
            "payload": {
                "token": picture_token
            }
        }]
    answer_text = f"Расписание на неделю"
    return answer_text, answer_payloads
