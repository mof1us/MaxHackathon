import datetime
import locale
import logging
from xmlrpc.client import DateTime

from bot.api.schedule_api import get_all_available_days
from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from data_types.Schedule import Schedule

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


def add_share_button(builder: InlineKeyboardBuilder, schedule_id: int, current_date:datetime.date, is_schedule_added: bool):
    if is_schedule_added:
        builder.row(
            CallbackButton(
                text="Поделиться этим расписанием",
                payload=str(
                    {
                        "type": "share_current_schedule",
                        "s_id": schedule_id,
                        "c_date": current_date.isoformat()
                    }
                ),
            )
        )
        return
    builder.row(
        CallbackButton(
            text="Добавить расписание",
            payload=str(
                {
                    "type": "add_current_schedule",
                    "s_id": schedule_id,
                    "c_date": current_date.isoformat()
                }
            ),
        )
    )


def schedule_month_select(
    schedule_id: int, current_date: datetime.date, busy_days: list[datetime.date]
):
    builder = InlineKeyboardBuilder()
    months = set()
    for day in busy_days:
        months.add(day.month)

    for month in months:
        builder.row(
            CallbackButton(
                text=datetime.date(1900, month, 1).strftime("%B"),
                payload=str(
                    {
                        "type": "schedule_week_select",
                        "s_id": schedule_id,
                        "c_date": current_date.replace(day=1, month=month).isoformat(),
                    }
                ),
            )
        )

    builder.row(
        CallbackButton(
            text="Назад",
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": current_date.isoformat(),
                }
            ),
        )
    )
    return builder.as_markup()


def schedule_week_select(
    schedule_id: int, current_date: datetime.date, busy_days: list[datetime.date]
):
    builder = InlineKeyboardBuilder()

    weeks = dict()
    for day in busy_days:
        first_day_of_week = day - datetime.timedelta(days=day.weekday())
        last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
        if (
            day.month != current_date.month
            and current_date.month != first_day_of_week.month
            and current_date.month != last_day_of_week.month
        ):
            continue
        first_day_of_first_week = day.replace(day=1) - datetime.timedelta(days=day.replace(day=1).weekday())
        week_i = (day - first_day_of_first_week).days // 7
        weeks[week_i] = (first_day_of_week, f"{first_day_of_week.day} {first_day_of_week.strftime("%b")}. - {last_day_of_week.day} {last_day_of_week.strftime("%b")}.")
    
    for w in weeks:
        builder.row(
            CallbackButton(
                text=f"Неделя {w} ({weeks[w][1]})",
                payload=str(
                    {
                        "type": "schedule_display",
                        "s_id": schedule_id,
                        "c_date": weeks[w][0].isoformat(),
                    }
                ),
            )
        )

    builder.row(
        CallbackButton(
            text="Назад",
            payload=str(
                {
                    "type": "schedule_month_select",
                    "s_id": schedule_id,
                    "c_date": datetime.datetime.now().isoformat(),
                }
            ),
        )
    )
    return builder.as_markup()


def day2week_idx(day:datetime.datetime):
    first_day_of_week = day - datetime.timedelta(days=day.weekday())
    last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
    first_day_of_first_week = day.replace(day=1) - datetime.timedelta(days=day.replace(day=1).weekday())
    week_i = (day - first_day_of_first_week).days // 7
    return week_i


def schedule_display(
    schedule_id: int, current_date: datetime.datetime, available_days: list[datetime.date], is_schedule_added: bool = False
):
    builder = InlineKeyboardBuilder()

    def is_available(date: datetime.date)->bool:
        return any(list(map(lambda x: x==date, available_days)))

    start_of_week = current_date - datetime.timedelta(days=current_date.weekday())

    
    current_week_i = day2week_idx(current_date)
    current_i = current_week_i+5*current_date.month
    available_days_on_week = {}
    weeks = {}
    for day in available_days:
        first_day_of_week = day - datetime.timedelta(days=day.weekday())
        week_i = day2week_idx(day)
        i = week_i+5*day.month
        if i == current_i and day.weekday() != 6:
            available_days_on_week[day.weekday()] = day
        weeks[i] = first_day_of_week
    
    weeks[current_i] = current_date - datetime.timedelta(days=current_date.weekday())
    
    prev_i = current_i
    next_i = current_i
    for i in weeks:
        # logging.info(">"*10 + str(i) + f" {current_i}")
        if current_i - i > 0:
            prev_i = i
        if i - current_i > 0:
            next_i = i
            break
    
    builder.row(
        CallbackButton(
            text="⬅️" if prev_i != current_i else '🚫', #
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": weeks[prev_i].isoformat(),
                }
            ),
        ),
        CallbackButton(
            text="📆",
            payload=str(
                {
                    "type": "schedule_month_select",
                    "s_id": schedule_id,
                    "c_date": current_date.isoformat(),
                }
            ),
        ),
        CallbackButton(
            text="➡️" if next_i != current_i else '🚫',
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": weeks[next_i].isoformat(),
                }
            ),
        ),
    )

    callback_row = []
    for i in range(6):
        day = available_days_on_week.get(i, None)
        callback_row.append(CallbackButton(
            text='🚫' if day is None else day.strftime("%a"),
            payload=str(
                {
                    "type": "schedule_display" if day is None else "schedule_day_display",
                    "s_id": schedule_id,
                    "c_date": current_date.isoformat() if day is None else day.isoformat(),
                }
            ),
        ))

    builder.row(*callback_row)
    add_share_button(builder, schedule_id, current_date, is_schedule_added)
    builder.row(
        CallbackButton(
            text="Назад",
            payload=str(
                {
                    "type": "schedule_list",
                }
            ),
        )
    )

    return builder.as_markup()


def schedule_day_display(
    schedule_id: int, current_date: datetime.date, available_days: list[datetime.date], is_schedule_added: bool = False
):
    builder = InlineKeyboardBuilder()

    # logging.info(f"{'<'*20} {len(available_days)}")
    if isinstance(current_date, datetime.datetime):
        current_date = current_date.date()
    prev_day = current_date
    next_day = current_date
    for day in available_days:
        # logging.info(">"*20 + day.isoformat() + f" {current_date.isoformat()}")
        if (current_date - day).total_seconds() > 0:
            prev_day = day
        if (day - current_date).total_seconds() > 0:
            next_day = day
            break

    builder.row(
        CallbackButton(
            text="⬅️" if prev_day != current_date else '🚫',
            payload=str(
                {
                    "type": "schedule_day_display",
                    "s_id": schedule_id,
                    "c_date": prev_day.isoformat(),
                }
            ),
        ),
        CallbackButton(
            text="➡️" if next_day != current_date else '🚫',
            payload=str(
                {
                    "type": "schedule_day_display",
                    "s_id": schedule_id,
                    "c_date": next_day.isoformat(),
                }
            ),
        ),
    )

    add_share_button(builder, schedule_id, current_date, is_schedule_added)

    builder.row(
        CallbackButton(
            text="Назад",
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": current_date.isoformat(),
                }
            ),
        )
    )

    return builder.as_markup()

def share_schedule_menu(schedule_id: int, current_date:datetime.date):
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(
            text="Назад",
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": current_date.isoformat(),
                }
            ),
        )
    )
    return builder.as_markup()