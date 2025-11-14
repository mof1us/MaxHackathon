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

def schedule_add_search_steps(search_q:str = "", search_results: list[tuple[str, str]] = [], addition_allowed: bool = False):
    builder = InlineKeyboardBuilder()
    search_results_display(builder, search_results)
    if search_q != "" and len(search_results) == 0 and addition_allowed:
        builder.row(CallbackButton(text="Добавить", payload=str({"type": "search_add_entry", "entry_name": search_q})))
    builder.row(CallbackButton(text="Отмена", payload=str({"type": "add_schedule"})))
    return builder.as_markup()

def schedule_add_from_ics_name_step():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Отмена", payload=str({"type": "add_schedule"})))
    return builder.as_markup()