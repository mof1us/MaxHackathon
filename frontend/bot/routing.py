from datetime import datetime
import json

from maxapi.types import BotStarted, Command, MessageCreated, MessageCallback, PhotoAttachmentRequestPayload
from maxapi import Bot, Dispatcher
from maxapi.filters import F
import os
from dotenv import load_dotenv
import logging
from maxapi import Bot, Dispatcher
from maxapi.types import (
    BotStarted,
    MessageCreated,
    MessageCallback,
)
from maxapi.types.attachments import Image
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types.attachments.attachment import OtherAttachmentPayload
from maxapi.types.attachments.file import File
from bot.menus.schedule.schedule_add.schedule_add import (
    add_schedule,
    schedule_add_from_ics,
    schedule_add_from_ics_name_step,
    schedule_add_search_steps,
    schedule_add_from_token,
)
from bot.menus.schedule.schedule_display.schedule_display import (
    schedule_display,
    schedule_week_select,
    schedule_month_select,
    schedule_day_display,
)
from bot.menus.schedule.schedule_list import schedule_list
from bot.menus.startup_menu import startup_menu
from data_types.Schedule import Schedule
import random

from database.entities.UserMenuEntity import UserMenuEntity
from database.services.UserService import UserService

logging.basicConfig(level=logging.INFO)

load_dotenv()
token = os.getenv("MAX_TOKEN")
if token is None:
    raise ValueError("MAX_TOKEN is not set")
bot = Bot(
    token,
)
dp = Dispatcher()
usrv = UserService()


async def main():  # точка входа
    await dp.start_polling(bot)


@dp.bot_started()
async def hello(event: BotStarted):
    await bot.send_message(
        chat_id=event.chat_id,
        text="Привет!",
        attachments=[
            startup_menu(),
        ],  # Для MAX клавиатура это вложение,
    )


@dp.message_created(F.message.body.attachments)
async def upload_callback(event: MessageCreated):
    # print("Attachement callback activated")
    atts = event.message.body.attachments
    if atts is None or len(atts) > 1:
        await event.message.answer("Пока отправка более одного вложения невозможна")
        return
    if event.message.recipient.chat_id is None:
        return
    u_state = usrv.get_user(event.message.recipient.chat_id)
    if u_state is None:
        # await event.message.answer("Пожалуйста, начните сначала")
        await event.message.answer("Загрузка файла не предполагалась в этом меню.")
        return
    # print(u_state.position)
    if u_state.position == "schedule_add_from_ics":
        att = atts[0]
        if not isinstance(att, File) or not isinstance(
                att.payload, OtherAttachmentPayload
        ):
            await event.message.answer("Пожалуйста, загрузите ICS файл")
            return
        ret_menu = schedule_add_search_steps()
        update_user(
            UserMenuEntity(
                id=event.message.recipient.chat_id,
                position="schedule_add_from_ics_search_university",
                metadata={"ics_url": att.payload.url},
            )
        )
        await event.message.answer("Какой-то умный текст", attachments=[ret_menu])

        print("-" * 10)
        print(att.payload.url)
        print("-" * 10)
        return
    await event.message.answer("Загрузка файла не предполагалась в этом меню.")


@dp.message_created(F.message.body.text)
async def text_callback(event: MessageCreated):
    # u_state = usrv.get_user(event.message.body.chat_id)
    # print("Craete callback activated")
    if event.message.recipient.chat_id is None:
        return
    u_state = usrv.get_user(event.message.recipient.chat_id)
    if u_state is None:
        await event.message.answer("Ваш ввод не предполагалась в этом меню.")
        return
    # print(u_state.position)
    if u_state.position == "schedule_add_from_ics_search_university":
        q = event.message.body.text
        if q is None:
            q = ""
        print(q)
        # Search logic
        ret_menu = schedule_add_search_steps(
            search_q=q if q is not None else "", addition_allowed=True
        )
        await event.message.answer("Какой-то умный текст", attachments=[ret_menu])
        return
    if u_state.position == "schedule_add_from_ics_name_step":
        q = event.message.body.text
        print(q)
        await event.message.answer("Добавляем расписание...")
        # Logic here
        s_id = 0
        ret_menu = schedule_display(
            schedule_id=int(s_id),
            current_date=datetime.now(),
        )
        await event.message.answer("unknown text", attachments=[ret_menu])
    if u_state.position == "schedule_add_from_token":
        q = event.message.body.text
        print(q)
        await event.message.answer("Добавляем расписание...")
        # Logic here
        s_id = 0
        ret_menu = schedule_display(
            schedule_id=int(s_id),
            current_date=datetime.now(),
        )
        await event.message.answer("unknown text 2", attachments=[ret_menu])
    if u_state.position == "schedule_add_from_std_university_search":
        q = event.message.body.text
        print(q)
        # Search logic

        ret_menu = schedule_add_search_steps(
            search_q=q if q is not None else "", search_results=[("М-да", "1")]
        )
        await event.message.answer(
            "Они надеялись найти ВУЗы...", attachments=[ret_menu]
        )
        return
    if u_state.position == "schedule_add_from_std_name_search":
        q = event.message.body.text
        print(q)
        # Search logic

        ret_menu = schedule_add_search_steps(
            search_q=q if q is not None else "", search_results=[("М-да", "1")]
        )
        await event.message.answer(
            "Они надеялись найти Расписание...", attachments=[ret_menu]
        )
        return


@dp.message_callback()
async def message_callback(event: MessageCallback):
    answer_text = "unknown_text"
    answer_payloads = [startup_menu()]

    try:
        payload = (
            json.loads(event.callback.payload.replace("'", '"'))
            if event.callback.payload
            else {"type": "undefined"}
        )
    except Exception as e:
        print("-" * 20 + "Parse exception" + "-" * 20)
        print(event.callback.payload)
        print("^" * 20 + "Parse exception" + "^" * 20)
    if payload["type"] == "schedule_list":
        answer_payloads = [schedule_list(
            schedules=[
                Schedule(id=0, name="Расписание 1"),
                Schedule(id=1, name="Расписание 2"),
                Schedule(id=2, name="Расписание 3"),
                Schedule(id=3, name="Расписание 4"),
                Schedule(id=4, name="Расписание 5"),
                Schedule(id=5, name="Расписание 6"),
                Schedule(id=6, name="Расписание 7"),
                Schedule(id=7, name="Расписание 8"),
            ],
            page=int(payload.get("page", 0)),
        )]
    elif payload["type"] == "schedule_display":
        answer_payloads = [schedule_display(
            schedule_id=int(payload["s_id"]),
            current_date=datetime.fromisoformat(payload["c_date"]),
        ), {
            "type": "image",
            "payload": {
                "token": "XPHZIEWVtMLTAYIDimeKs6fgfcm8fm6TM5DxIjZnGIXAxE5K9+Gbf6yVvfHeRBunrj2E76kCVv90VyAQ/bz5dj6BmnIOMoMof5Hh9Zf3//X13ah2JIsPs30/qY4l9UOx2ZW5SqU3n9XfRYinQhBgE8J17uwQEzQG"
            }
        }]
        answer_text = f"Date {payload['c_date']}"
    elif payload["type"] == "schedule_day_display":
        answer_payloads = [schedule_day_display(
            schedule_id=int(payload["s_id"]),
            current_date=datetime.fromisoformat(payload["c_date"]),
        )]
        answer_text = f"Date day {payload['c_date']}"
    elif payload["type"] == "schedule_week_select":
        answer_payloads = [schedule_week_select(
            schedule_id=int(payload["s_id"]),
            current_date=datetime.fromisoformat(payload["c_date"]),
            busy_days=sorted(
                list(
                    set(
                        [
                            datetime(2025, random.randint(1, 12), random.randint(1, 28))
                            for i in range(60)
                        ]
                    )
                )
            ),
        )]
        answer_text = f"Date {payload['c_date']}"
        # answer_menu = schedule_week_select(schedule_id=int(payload["s_id"]), current_date=datetime.fromisoformat(payload["c_date"]), busy_days=sorted([datetime(2025, 6, i) for i in range(3, 31)]))
    elif payload["type"] == "schedule_month_select":
        answer_payloads = [schedule_month_select(
            schedule_id=int(payload["s_id"]),
            current_date=datetime.fromisoformat(payload["c_date"]),
            busy_days=sorted(
                list(
                    set(
                        [
                            datetime(2025, random.randint(1, 12), random.randint(1, 28))
                            for i in range(60)
                        ]
                    )
                )
            ),
        )]
        answer_text = f"Date {payload['c_date']}"
        # answer_menu = schedule_month_select(schedule_id=int(payload["s_id"]), current_date=datetime.fromisoformat(payload["c_date"]), busy_days=sorted([datetime(2025, 6, i) for i in range(3, 31)]))
    elif payload["type"] == "add_schedule":
        answer_payloads = [add_schedule()]
        if event.message.recipient.chat_id is not None:
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id, position="", metadata={}
                )
            )
    elif payload["type"] == "schedule_add_from_std":
        if event.message.recipient.chat_id is None:
            return
        answer_text = "Искать он тут ВУЗ собрался, ага"
        answer_payloads = [schedule_add_search_steps()]
        update_user(
            UserMenuEntity(
                id=event.message.recipient.chat_id,
                position="schedule_add_from_std_university_search",
                metadata={},
            )
        )
    elif payload["type"] == "schedule_add_from_token":
        answer_payloads = [schedule_add_from_token()]
        if event.message.recipient.chat_id is None:
            return
        update_user(
            UserMenuEntity(
                id=event.message.recipient.chat_id,
                position="schedule_add_from_token",
                metadata={},
            )
        )

    elif payload["type"] == "schedule_add_from_ics":
        if event.message.recipient.chat_id is None:
            return
        update_user(
            UserMenuEntity(
                id=event.message.recipient.chat_id,
                position="schedule_add_from_ics",
                metadata={},
            )
        )
        answer_payloads = [schedule_add_from_ics()]
        answer_text = "Загрузите ICS файл"
    elif payload["type"] == "search_result":
        if event.message.recipient.chat_id is None:
            return
        u_data = usrv.get_user(event.message.recipient.chat_id)
        if u_data is None:
            return
        u_pos = u_data.position
        if u_pos == "schedule_add_from_ics_search_university":
            university_id = int(payload["result_payload"])
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id,
                    position="schedule_add_from_ics_name_step",
                    metadata={**u_data.metadata, "university_id": university_id},
                )
            )
            answer_payloads = [schedule_add_from_ics_name_step()]
        if u_pos == "schedule_add_from_std_university_search":
            university_id = int(payload["result_payload"])
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id,
                    position="schedule_add_from_std_name_search",
                    metadata={**u_data.metadata, "university_id": university_id},
                )
            )
            answer_text = "Расписание ищешь?"
            answer_payloads = [schedule_add_search_steps()]
        if u_pos == "schedule_add_from_std_name_search":
            s_id = int(payload["result_payload"])
            # Adition logic here
            answer_payloads = [schedule_display(
                schedule_id=s_id, current_date=datetime.now()
            )]

    elif payload["type"] == "search_add_entry":
        if event.message.recipient.chat_id is None:
            return
        u_data = usrv.get_user(event.message.recipient.chat_id)
        if u_data is None:
            return
        u_pos = u_data.position
        if u_pos == "schedule_add_from_ics_search_university":
            await event.message.answer("Добавляем новый ВУЗ...")
            university_name = payload["entry_name"]
            # Adition logic here
            university_id = 0
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id,
                    position="schedule_add_from_ics_name_step",
                    metadata={**u_data.metadata, "university_id": university_id},
                )
            )
            answer_payloads = [schedule_add_from_ics_name_step()]
            await event.message.answer(answer_text, attachments=answer_payloads)
            return

    elif payload["type"] == "settings":
        answer_text = "настройки"
    else:
        answer_payloads = [startup_menu()]
        if event.message.recipient.chat_id is not None:
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id, position="", metadata={}
                )
            )
    PhotoAttachmentRequestPayload()
    await event.answer(attachments=answer_payloads, new_text=answer_text)


def update_user(new_data: UserMenuEntity) -> bool:
    user = usrv.get_user(new_data.id)
    if user is None:
        return usrv.create_user(new_data)
    return usrv.change_user(new_data)
