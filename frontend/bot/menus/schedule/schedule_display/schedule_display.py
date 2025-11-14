import datetime
import locale
from xmlrpc.client import DateTime
from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from data_types.Schedule import Schedule

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


def add_share_button(builder: InlineKeyboardBuilder, is_schedule_added: bool):
    if is_schedule_added:
        builder.row(
            CallbackButton(
                text="Поделиться этим расписанием",
                payload=str(
                    {
                        # TODO: Make propper payload
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
                    # TODO: Make propper payload
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
        print(day, first_day_of_first_week, (day - first_day_of_first_week).days)
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


def schedule_display(
    schedule_id: int, current_date: datetime.date, is_schedule_added: bool = False
):
    builder = InlineKeyboardBuilder()

    available_weeks = []

    builder.row(
        CallbackButton(
            text="⬅️",
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": (current_date - datetime.timedelta(days=7)).isoformat(),
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
            text="➡️",
            payload=str(
                {
                    "type": "schedule_display",
                    "s_id": schedule_id,
                    "c_date": (current_date + datetime.timedelta(days=7)).isoformat(),
                }
            ),
        ),
    )

    start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
    builder.row(
        *[
            CallbackButton(
                text=(start_of_week + datetime.timedelta(days=i)).strftime("%a"),
                payload=str(
                    {
                        "type": "schedule_day_display",
                        "s_id": schedule_id,
                        "c_date": (
                            start_of_week + datetime.timedelta(days=i)
                        ).isoformat(),
                    }
                ),
            )
            for i in range(7)
        ]
    )
    add_share_button(builder, is_schedule_added)
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
    schedule_id: int, current_date: datetime.date, is_schedule_added: bool = False
):
    builder = InlineKeyboardBuilder()

    builder.row(
        CallbackButton(
            text="⬅️",
            payload=str(
                {
                    "type": "schedule_day_display",
                    "s_id": schedule_id,
                    "c_date": (current_date - datetime.timedelta(days=1)).isoformat(),
                }
            ),
        ),
        CallbackButton(
            text="➡️",
            payload=str(
                {
                    "type": "schedule_day_display",
                    "s_id": schedule_id,
                    "c_date": (current_date + datetime.timedelta(days=1)).isoformat(),
                }
            ),
        ),
    )

    add_share_button(builder, is_schedule_added)

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
