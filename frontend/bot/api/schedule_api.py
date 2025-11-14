import datetime
import logging
import os
import aiohttp
from dotenv import load_dotenv

from data_types.Schedule import Schedule

load_dotenv()


async def get_schedule_token(schedule_id: int, week_start: datetime.datetime, flag: str = "week"):
    async with aiohttp.ClientSession() as session:
        async with session.post(os.getenv("SCHEDULE_API") + "token",
            json={
                "schedule_id": schedule_id,
                "week_start": week_start.isoformat() + "Z",
                "flag": flag
            }) as response:
            result = await response.json()
            logging.info(str(result))
            return result["token"]

async def get_schedule_list(user_id: int) -> list[Schedule]:
    schedules_list = []
    async with aiohttp.ClientSession() as session:
        async with session.get(os.getenv("SCHEDULE_API") + f"users/{user_id}/schedules",) as response:
            if response.status != 200:
                return []
            result = await response.json()
            for i in result:
                logging.info(f"i = {i}", )
                schedules_list.append(Schedule(
                    id=i["id"],
                    name=i["name"],
                ))
    return schedules_list