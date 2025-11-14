import hashlib
import os

from html2image import Html2Image

from CONSTANTS import TEMP_FILES_LIMIT
from application.responses.DayScheduleGenerationRequest import DayScheduleGenerationRequest
from application.responses.WeekScheduleGeneratorRequest import WeekScheduleGeneratorRequest
from template_generator.Templator import Templator


def get_hash(value: int) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()


def counter():
    c = 0
    while True:
        yield c
        c += 1
    return c


class ScreenShooter:
    def __init__(self):
        self.hti = Html2Image(
            output_path="/app/out",
            browser_executable="/usr/bin/google-chrome-stable",
            # важные флаги для контейнеров
            custom_flags=[
                "--headless=new",
                "--no-sandbox",  # если запускаете под root
                "--disable-dev-shm-usage",  # меньше падений в Docker
                "--hide-scrollbars",
            ],
        )
        self.templator = Templator()
        self.counter = counter()

    def __calculate_week_page_height(self, week: WeekScheduleGeneratorRequest):
        days = week.days
        height = 0
        def is_inside(idx):
            return len(days) > idx

        for i in range(3):
            count_top, count_bottom = (
                len(days[i].item_list) if is_inside(i) else 0,
                len(days[i + 3].item_list) if is_inside(i + 3) else 0)
            height = max((max(count_top, 5) + max(count_bottom, 5)) * 155 + 135, height)
        print("page height: ", height)
        return height

    def __calculate_day_page_height(self, day: DayScheduleGenerationRequest):
        height = (max(len(day.item_list), 5)) * 155 + 135
        return height

    def make_week_screenshot(self, week: WeekScheduleGeneratorRequest):
        file_id = next(self.counter)
        filename = get_hash(file_id)

        file_to_delete = os.path.join("out", get_hash(file_id - TEMP_FILES_LIMIT))
        if os.path.exists(file_to_delete + ".jpg"):
            os.remove(file_to_delete + ".jpg")
            os.remove(file_to_delete + ".html")  # удаление старых файлов

        self.templator.get_rendered_week_template(filename + ".html", week)
        self.hti.screenshot(html_file="out/" + filename + ".html",
                            save_as=filename + ".jpg", size=(1400, self.__calculate_week_page_height(week)))
        return filename + ".jpg"

    def make_day_screenshot(self, day: DayScheduleGenerationRequest):
        file_id = next(self.counter)
        filename = get_hash(file_id)
        file_to_delete = os.path.join("out", get_hash(file_id - TEMP_FILES_LIMIT))
        if os.path.exists(file_to_delete + ".jpg"):
            os.remove(file_to_delete + ".jpg")
            os.remove(file_to_delete + ".html")

        self.templator.get_rendered_day_template(filename + ".html", day)
        self.hti.screenshot(html_file="out/" + filename + ".html",
                            save_as=filename + ".jpg", size=(1400, self.__calculate_day_page_height(day)))
        return filename + ".jpg"