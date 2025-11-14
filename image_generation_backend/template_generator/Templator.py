from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape

from application.responses.WeekScheduleGeneratorRequest import WeekScheduleGeneratorRequest


class Templator:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader('static/templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.template = self.env.get_template('week_scedule_template.jinja')

    def __change_time_formats(self, week: WeekScheduleGeneratorRequest):
        for i in range(len(week.days)):
            for j in range(len(week.days[i].item_list)):
                start_time = datetime.fromisoformat(week.days[i].item_list[j].start_time[:-1])
                end_time = datetime.fromisoformat(week.days[i].item_list[j].start_time[:-1])
                week.days[i].item_list[j].start_time = start_time.strftime("%H:%M")
                week.days[i].item_list[j].end_time = end_time.strftime("%H:%M")
                print(week.days[i].item_list[j].start_time, week.days[i].item_list[j].end_time)

    def get_rendered_template(self, filename: str, response: WeekScheduleGeneratorRequest):
        self.__change_time_formats(response)
        rendered = self.template.render(
                name=response.name,
                days=response.days,
        )
        with open("out/" + filename, "w") as f:
            f.write(rendered)
            f.close()
