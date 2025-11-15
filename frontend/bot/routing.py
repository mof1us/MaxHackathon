from datetime import datetime
import json

from bot.ui.display_schedule import display_schedule
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
from maxapi.types.message import Message
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
    succes_addition,
)
from bot.menus.schedule.schedule_display.schedule_display import (
    schedule_display,
    schedule_week_select,
    schedule_month_select,
    schedule_day_display,
    share_schedule_menu,
)
from bot.menus.schedule.schedule_list import schedule_list
from bot.menus.startup_menu import startup_menu
from data_types.Schedule import Schedule

from database.entities.UserMenuEntity import UserMenuEntity
from database.services.UserService import UserService

from bot.api.schedule_api import connect_user_to_schedule, get_all_available_days, get_schedule_token, search_university, add_schedule_from_ics, create_university, \
    search_schedule_university

from bot.api.schedule_api import get_schedule_list

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
        text="Привет! \n\nЯ - бот, который поможет ознакомиться с расписанием в университете. \n\nЯ умею:\n" + \
        "👉 Отображать расписания в удобном формате\n" + \
        "👉 Обрабатывать и сохранять расписания из ics файлов\n" + \
        "👉 Хранить любые расписания из вашего университета (просто воспользуйтесь поиском!)\n\n" +\
        "Данный бот является решением команды 'MAXимально не по тз' в рамках хакатона.",
        attachments=[
            startup_menu(),
        ],  # Для MAX клавиатура это вложение,
    )


@dp.message_created(F.message.body.attachments)
async def upload_callback(event: MessageCreated):
    # print("Attachement callback activated")
    atts = event.message.body.attachments
    if atts is None or len(atts) > 1:
        await event.message.answer("⚠️Загрузите один файл⚠️")
        return
    if event.message.recipient.chat_id is None:
        return
    u_state = usrv.get_user(event.message.recipient.chat_id)
    if u_state is None:
        # await event.message.answer("Пожалуйста, начните сначала")
        await event.message.answer("⚠️Я вас не понял⚠️")
        return
    # print(u_state.position)
    if u_state.position == "schedule_add_from_ics":
        att = atts[0]
        if not isinstance(att, File) or not isinstance(
                att.payload, OtherAttachmentPayload
        ):
            await event.message.answer("⚠️Загрузите файл в формате ICS⚠️")
            return

        ret_menu = schedule_add_search_steps()
        update_user(
            UserMenuEntity(
                id=event.message.recipient.chat_id,
                position="schedule_add_from_ics_search_university",
                metadata={"ics_url": att.payload.url},
            )
        )
        await event.message.answer("✍️Введите название университета🏫", attachments=[ret_menu])

        print("-" * 10)
        print(att.payload.url)
        print("-" * 10)
        return
    await event.message.answer("⚠️Я вас не понял⚠️")


@dp.message_created(F.message.body.text)
async def text_callback(event: MessageCreated):
    # u_state = usrv.get_user(event.message.body.chat_id)
    # print("Craete callback activated")
    if event.message.recipient.chat_id is None:
        return
    u_state = usrv.get_user(event.message.recipient.chat_id)
    if u_state is None:
        await event.message.answer("⚠️Я вас не понял⚠️")
        return
    # print(u_state.position)
    if u_state.position == "schedule_add_from_ics_search_university":
        q = event.message.body.text
        if q is None:
            q = ""
        universities_by_query = await search_university(event.message.body.text)

        ret_menu = schedule_add_search_steps(
            search_results=universities_by_query,
            search_q=q if q is not None else "", addition_allowed=True
        )
        await event.message.answer("Выберите ваш университет🏫 из списка (или используйте как новый✨)", attachments=[ret_menu])
        return
    if u_state.position == "schedule_add_from_ics_name_step":
        q = event.message.body.text
        await event.message.answer("⌛Добавляем расписание...⌛")
        # Logic here
        user = usrv.get_user(event.message.recipient.chat_id)
        if user is None:
            await send_error("⚠️Произошла неизвестная ошибка, попробуйте позже⚠️", event.message)
            return
        s_id = await add_schedule_from_ics(user.metadata["ics_url"], q, event.message.recipient.chat_id, user.metadata["university_id"])
        if s_id is None:
            await send_error("⚠️Произошла неизвестная ошибка при обработке файла, попробуйте позже⚠️", event.message)
            return
    
        available_days = await get_all_available_days(s_id) 
        
        # answer_text, answer_payloads = await display_schedule(datetime.now().isoformat(), s_id, "week", True, available_days)
        answer_text = f"Расписание успешно добавлено! Его id: {s_id}"
        answer_payloads = [succes_addition(s_id)]
        await event.message.answer(answer_text, attachments=answer_payloads)
    if u_state.position == "schedule_add_from_token":
        q = event.message.body.text
        try:
            s_id = int(q)
        except TypeError:
            await event.message.answer("⚠️Не верный ID⚠️")
            return
        await event.message.answer("Добавляем расписание...")
        # logging.info(f"Connecting user {event.message.recipient.chat_id} to schedule {s_id}")
        is_success = await connect_user_to_schedule(event.message.recipient.chat_id, s_id)
        if not is_success:
            await send_error("⚠️Не удалось добавить расписание в ваш аккаунт⚠️", event.message)
            return
        available_days = await get_all_available_days(s_id)

        # answer_text, answer_payloads = await display_schedule(datetime.now().isoformat(), s_id, "week", True, available_days)
        answer_text = f"Расписание успешно добавлено!"
        answer_payloads = [succes_addition(s_id)]
        await event.message.answer(answer_text, attachments=answer_payloads)
    if u_state.position == "schedule_add_from_std_university_search":
        q = event.message.body.text
        unis = await search_university(q)
        ret_menu = schedule_add_search_steps(
            search_q=q if q is not None else "", search_results=unis
        )
        "Выберите университет" if len(unis) > 0 else "⚠️Ничего не найдено⚠️"
        if q and len(unis) > 0:
            ans_text = "☝Выберите университет🏫"
        elif q:
            ans_text = "⚠️Ничего не найдено, правильно имя ВУЗа пиши или добавь его⚠️"
        else:
            ans_text = "Начните печтатать название ВУЗа🏫"
        await event.message.answer(
            ans_text, attachments=[ret_menu]
        )
        return
    if u_state.position == "schedule_add_from_std_name_search":
        q = event.message.body.text
        user = usrv.get_user(event.message.recipient.chat_id)
        if user is None:
            await send_error("⚠️Произошла неизвестная ошибка, попробуйте позже⚠️", event.message)
            return
        schedules = await search_schedule_university(user.metadata["university_id"], q)
        ret_menu = schedule_add_search_steps(
            search_q=q if q is not None else "", search_results=schedules
        )
        await event.message.answer(
            "📅Найденные расписания", attachments=[ret_menu]
        )
        return


@dp.message_callback()
async def message_callback(event: MessageCallback):
    answer_text, stp_menu = main_menu()
    answer_payloads = [stp_menu]

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
        answer_text = "📌Это раздел с расписаниями.\nЗдесь вы можете перейти в интересующее вас расписвние и 👀посмотреть👀 его. \nНе пугайтесь, если здесь пусто, вы можете добавить новое расписание, воспользовавшись кнопкой 'Добавить'💗"
        answer_payloads = [schedule_list(
            schedules=await get_schedule_list(event.message.recipient.chat_id),
            # schedules=[
            #     Schedule(id=0, name="Расписание 1"),
            #     Schedule(id=1, name="Расписание 2"),
            #     Schedule(id=2, name="Расписание 3"),
            #     Schedule(id=3, name="Расписание 4"),
            #     Schedule(id=4, name="Расписание 5"),
            #     Schedule(id=5, name="Расписание 6"),
            #     Schedule(id=6, name="Расписание 7"),
            #     Schedule(id=7, name="Расписание 8"),
            # ],
            page=int(payload.get("page", 0)),
        )]
    elif payload["type"] == "share_current_schedule":
        schedule_id = int(payload["s_id"])
        answer_text = f"🛠️Id текущего расписания: {schedule_id}. 📨Отправьте его, другому пользователю, чтобы он смог добавить расписание."
        answer_payloads = [share_schedule_menu(schedule_id, datetime.fromisoformat(payload["c_date"]))]
    elif payload["type"] == "schedule_display" or payload["type"] == "add_current_schedule":
        schedule_id = int(payload["s_id"])
        if payload["type"] == "add_current_schedule":
            is_success = await connect_user_to_schedule(event.message.recipient.chat_id, schedule_id)
            if not is_success:
                await event.message.answer("⚠️Не удалось добавить расписание в ваш аккаунт⚠️")
                
        schedules = await get_schedule_list(event.message.recipient.chat_id)
        available_days = await get_all_available_days(schedule_id)
        

        answer_text, answer_payloads = await display_schedule(payload['c_date'], schedule_id, "week", schedule_id in [s.id for s in schedules], available_days)
    elif payload["type"] == "schedule_day_display":
        schedule_id = int(payload["s_id"])
        schedules = await get_schedule_list(event.message.recipient.chat_id)
        available_days = await get_all_available_days(schedule_id)
        answer_text, answer_payloads = await display_schedule(payload['c_date'], schedule_id, "day", schedule_id in [s.id for s in schedules], available_days)
    elif payload["type"] == "schedule_week_select":
        schedule_id = int(payload["s_id"])
        available_days = await get_all_available_days(schedule_id)
        answer_text = "Выбор недели"
        answer_payloads = [schedule_week_select(
            schedule_id=schedule_id,
            current_date=datetime.fromisoformat(payload["c_date"]),
            busy_days=available_days,
        )]
        
        
       
        # answer_menu = schedule_week_select(schedule_id=int(payload["s_id"]), current_date=datetime.fromisoformat(payload["c_date"]), busy_days=sorted([datetime(2025, 6, i) for i in range(3, 31)]))
    elif payload["type"] == "schedule_month_select":
        schedule_id = int(payload["s_id"])
        available_days = await get_all_available_days(schedule_id)
        answer_payloads = [schedule_month_select(
            schedule_id=schedule_id,
            current_date=datetime.fromisoformat(payload["c_date"]),
            busy_days=available_days,
        )]
        answer_text = f"Выбор месяца"
        # answer_menu = schedule_month_select(schedule_id=int(payload["s_id"]), current_date=datetime.fromisoformat(payload["c_date"]), busy_days=sorted([datetime(2025, 6, i) for i in range(3, 31)]))
    elif payload["type"] == "add_schedule":
        answer_text = "Текст добавления"
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
        answer_text = "𓂃🪶Введите название университета🏫"
        answer_payloads = [schedule_add_search_steps()]
        update_user(
            UserMenuEntity(
                id=event.message.recipient.chat_id,
                position="schedule_add_from_std_university_search",
                metadata={},
            )
        )
    elif payload["type"] == "schedule_add_from_token":
        answer_text = "Текст добавлдения по токену"
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
        answer_text = "🚀Загрузите ICS файл📄"
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
            answer_text = "Введите название расписания (группу, аудиторию или имя преподавателя)"
        if u_pos == "schedule_add_from_std_university_search":
            university_id = int(payload["result_payload"])
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id,
                    position="schedule_add_from_std_name_search",
                    metadata={**u_data.metadata, "university_id": university_id},
                )
            )
            answer_text = "✍Введите название расписание (номер группы👥, аудиторию🚪 или имя преподавателя💼)"
            answer_payloads = [schedule_add_search_steps()]
        if u_pos == "schedule_add_from_std_name_search":
            s_id = int(payload["result_payload"])
            available_days = await get_all_available_days(s_id)
            update_user(
                UserMenuEntity(
                    id=event.message.recipient.chat_id,
                    position="",
                    metadata={},
                )
            )
            schedules = await get_schedule_list(event.message.recipient.chat_id)
            answer_text, answer_payloads = await display_schedule(datetime.now().isoformat(), s_id, "week", s_id in [s.id for s in schedules], available_days)

    elif payload["type"] == "search_add_entry":
        if event.message.recipient.chat_id is None:
            return
        u_data = usrv.get_user(event.message.recipient.chat_id)
        if u_data is None:
            return
        u_pos = u_data.position
        if u_pos == "schedule_add_from_ics_search_university":
            await event.message.answer("🛠️Добавляем новый ВУЗ...🔨")
            university_name = payload["entry_name"]
            university_id = await create_university(university_name)
            answer_text = "Введите название расписания (например номер группы, номер аудитории или имя преподавателя)"

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
        answer_text = "Coming soon!"
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


def main_menu():
    answer_text = """📌Это главное меню.\nЧерез него ты можешь попасть в раздел 📅расписаний или перейти в ⚙️настройки.
    """
    return answer_text, startup_menu()



async def send_error(err_text:str, evt_msg: Message):
    await evt_msg.answer(err_text, attachments=[startup_menu()])
    update_user(
        UserMenuEntity(
            id=evt_msg.recipient.chat_id,
            position="",
            metadata={}
        )
    )