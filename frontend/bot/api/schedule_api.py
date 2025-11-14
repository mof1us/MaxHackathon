from datetime import datetime, date
import logging
import os
import aiohttp
from dotenv import load_dotenv

from data_types.Schedule import Schedule
from data_types.University import University

load_dotenv()


async def get_schedule_token(schedule_id: int, week_start: datetime, flag: str = "week"):
    async with aiohttp.ClientSession() as session:
        async with session.post(os.getenv("SCHEDULE_API") + "token",
            json={
                "schedule_id": schedule_id,
                "week_start": week_start.isoformat() + "Z",
                "flag": flag
            }) as response:
            # TODO: add error handling
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

async def search_university(query: str) -> list[University]:
    finded_universities = []
    async with aiohttp.ClientSession() as session:
        async with session.get(os.getenv("UNIVERSITIES_API") + f"universities?query={query}") as response:
            logging.info(str(response))
            if response.status != 200:
                return []
            result = await response.json()
            for i in result:
                finded_universities.append(University(
                    id=i["id"],
                    name=i["name"],
                ))
    return finded_universities

async def add_schedule_from_ics(ics_url: str, title: str, user: int, university: int) -> int | None:
    async with aiohttp.ClientSession() as session:
        async with session.post(os.getenv("SCHEDULE_API") + "schedule",
                                json={
                                    "link": ics_url,
                                    "schedule_name": title,
                                    "university_id": university,
                                    "user_id": user
                                }) as response:
            if response.status != 201:
                return None
            return (await response.json()).get("id")

async def create_university(uni_name: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(os.getenv("UNIVERSITIES_API") + f"universities?name={uni_name}") as response:
            return (await response.json()).get("id")

async def search_schedule_university(uni_id: int, query: str) -> list[Schedule]:
    async with aiohttp.ClientSession() as session:
        async with session.get(os.getenv("SCHEDULE_API") + f"schedule/resolve_list?id={uni_id}&name={query}&limit=5") as response:
            json_result = await response.json()
            schedule_list = list(map(lambda x: Schedule(id=x["id"], name=x["name"]), json_result))
            return schedule_list


async def get_all_available_days(schedule_id: int) -> list[date]:
    async with aiohttp.ClientSession() as session:
        async with session.get(os.getenv("SCHEDULE_API") + f"time/all/{schedule_id}",) as response:
            json_response = await response.json()

            logging.info(f"response: {json_response}")

            return [
                datetime.fromisoformat(d.replace("Z", "+00:00")).date()
                for d in json_response
            ]


async def connect_user_to_schedule(user_id: int, schedule_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(os.getenv("SCHEDULE_API") + f"schedule/attach", json={
            "schedule_id":schedule_id,
            "user_id":user_id
            }) as response:
            if response.status == 204:
                return True
            return False
            
