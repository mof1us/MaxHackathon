from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape

from application.responses.WeekScheduleGeneratorRequest import WeekScheduleGeneratorRequest
from application.responses.DayScheduleGenerationRequest import DayScheduleGenerationRequest


class Templator:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader('static/templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.week_template = self.env.get_template('week_scedule_template.jinja')
        self.day_template = self.env.get_template('schedule_day_template.jinja')

    def __change_week_time_formats(self, week: WeekScheduleGeneratorRequest):
        for i in range(len(week.days)):
            self.__change_day_time_formats(week.days[i])

    def __change_day_time_formats(self, day: DayScheduleGenerationRequest):
        for j in range(len(day.item_list)):
            start_time = datetime.fromisoformat(day.item_list[j].start_time[:-1])
            end_time = datetime.fromisoformat(day.item_list[j].end_time[:-1])
            day.item_list[j].start_time = start_time.strftime("%H:%M")
            day.item_list[j].end_time = end_time.strftime("%H:%M")
            print(day.item_list[j].start_time, day.item_list[j].end_time)

    def get_rendered_week_template(self, filename: str, response: WeekScheduleGeneratorRequest):
        self.__change_week_time_formats(response)
        rendered = self.week_template.render(
                name=response.name,
                days=response.days,
        )
        with open("out/" + filename, "w") as f:
            f.write(rendered)
            f.close()


    def get_rendered_day_template(self, filename: str, response: DayScheduleGenerationRequest):
        self.__change_day_time_formats(response)
        rendered = self.day_template.render(
            day_item=response
        )
        with open("out/" + filename, "w") as f:
            f.write(rendered)
            f.close()

