import uvicorn
from jinja2 import Environment, FileSystemLoader, select_autoescape
from html2image import Html2Image

from application.Application import Application

if __name__ == '__main__':
    app = Application()
    uvicorn.run(app.app, host='0.0.0.0', port=8000)
    # hti = Html2Image(
    #     output_path="/app/out",
    #     browser_executable="/usr/bin/google-chrome-stable",
    #     # важные флаги для контейнеров
    #     custom_flags=[
    #         "--headless=new",
    #         "--no-sandbox",  # если запускаете под root
    #         "--disable-dev-shm-usage",  # меньше падений в Docker
    #         "--hide-scrollbars",
    #     ],
    # )
    #
    #
    # env = Environment(
    #     loader=FileSystemLoader('static/templates'),
    #     autoescape=select_autoescape(['html', 'xml'])
    # )
    # template = env.get_template('schedule_template.jinja')
    # rendered = template.render(
    #     a_variable="test",
    #     navigation = [
    #         {
    #             "href": "aaa",
    #             "caption": "bbb"
    #         }
    #     ]
    # )
    # print("start screen")
    # hti.screenshot(url='https://www.python.org', save_as='python_org.png')
    # print("end screen")
    # print(rendered)