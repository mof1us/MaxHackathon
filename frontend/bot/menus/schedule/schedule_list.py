from dataclasses import dataclass
import datetime
from maxapi import Bot, Dispatcher
from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from data_types.Schedule import Schedule


def schedule_list(schedules: list[Schedule], page: int, entries_per_page: int = 5):
    builder = InlineKeyboardBuilder()

    total_pages = (
        (len(schedules) + entries_per_page - 1) // entries_per_page
        if schedule_list
        else 0
    )
    is_next_available = page < total_pages - 1
    is_prev_available = page > 0

    if len(schedules) < entries_per_page:
        display_schedules = schedules
    else:
        start_idx = page * entries_per_page
        end_idx = start_idx + entries_per_page
        display_schedules = schedules[start_idx:end_idx]

    for sc in display_schedules:
        builder.row(CallbackButton(text=sc.name, payload=str({
            "type": "schedule_display",
            "s_id": sc.id,
            "c_date": datetime.datetime.now().isoformat(),
        })))

    if len(schedules) > entries_per_page:
        prev_page_num = page - 1 if is_prev_available else page
        next_page_num = page + 1 if is_next_available else page

        builder.row(
            CallbackButton(
                text=f"{'⬅️' if is_prev_available else '⛔️'}",
                payload=str({"type": "schedule_list", "page": prev_page_num}),
            ),
            CallbackButton(
                text=f"{'➡️' if is_next_available else '⛔️'}",
                payload=str({"type": "schedule_list", "page": next_page_num}),
            ),
        )

    builder.row(CallbackButton(text="Добавить", payload=str({"type": "add_schedule"})))
    builder.row(CallbackButton(text="Назад", payload=str({"type": "main_menu"})))

    return builder.as_markup()
