import aiohttp
from fastapi import FastAPI
from application.ScreenShoter import ScreenShooter
from application.responses.WeekScheduleGeneratorRequest import WeekScheduleGeneratorRequest
import os
from dotenv import load_dotenv

load_dotenv()


async def upload_image(filename: str) -> str | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://platform-api.max.ru/uploads?type=image',
            headers={
                "Authorization": os.getenv("MAX_TOKEN"),
            }) as response:
                json_response = await response.json()
                print("response1: ", json_response)
                upload_url = json_response["url"]
        form = aiohttp.FormData()
        form.add_field(
            name='file',
            value=open("out/" + filename, 'rb'),
            filename='image.jpg',
            content_type='image/jpeg'
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(upload_url, data=form) as response:
                json_response = await response.json()
                hash_code = list(json_response["photos"].keys())[0]
                image_token = json_response["photos"][hash_code]["token"]
        return image_token
    except Exception as e:
        print("error while uploading image: ", e)
        return None


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.screen_shooter = ScreenShooter()
        self.setup_routes()

    def setup_routes(self):
        @self.app.post("/generate_week_schedule")
        async def generate_week_schedule(response: WeekScheduleGeneratorRequest):
            filename = self.screen_shooter.make_screenshot(response)
            max_image_token = await upload_image(filename)
            return {
                "token": max_image_token
            }
