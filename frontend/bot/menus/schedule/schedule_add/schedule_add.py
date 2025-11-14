from datetime import datetime
from data_types.Schedule import Schedule
from data_types.University import University
from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from bot.menus.schedule.schedule_add.search import search_results_display


def add_schedule():
    builder = InlineKeyboardBuilder()
    builder.add(
        CallbackButton(
            text="Добавить из загруженных в бызу вузов",
            payload=str({"type": "schedule_add_from_std"}),
        )
    )
    builder.row(
        CallbackButton(text="из ics", payload=str({"type": "schedule_add_from_ics"})),
        CallbackButton(
            text="по токену", payload=str({"type": "schedule_add_from_token"})
        ),
    )
    builder.row(CallbackButton(text="Назад", payload=str({"type": "schedule_list"})))
    return builder.as_markup()


def schedule_add_from_token():
    builder = InlineKeyboardBuilder()
    builder.add(CallbackButton(text="Отмена", payload=str({"type": "add_schedule"})))
    return builder.as_markup()


def schedule_add_from_ics():
    builder = InlineKeyboardBuilder()
    builder.add(CallbackButton(text="Отмена", payload=str({"type": "add_schedule"})))
    return builder.as_markup()

def schedule_add_search_steps(search_q:str = "", search_results: list[University] | list[Schedule] = [], addition_allowed: bool = False):
    builder = InlineKeyboardBuilder()
    search_results_display(builder, search_results)
    if search_q != "" and addition_allowed:
        builder.row(CallbackButton(text="Добавить", payload=str({"type": "search_add_entry", "entry_name": search_q})))
    builder.row(CallbackButton(text="Отмена", payload=str({"type": "add_schedule"})))
    return builder.as_markup()

def schedule_add_from_ics_name_step():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Отмена", payload=str({"type": "add_schedule"})))
    return builder.as_markup()

def succes_addition(schedule_id:int):
    builder = InlineKeyboardBuilder()
    builder.add(CallbackButton(text="к списку", payload=str({"type": "schedule_list"})))
    builder.add(CallbackButton(text="к расписанию", payload=str({"type": "schedule_display", "s_id": schedule_id, "c_date": datetime.now().isoformat()})))
    return builder.as_markup()
