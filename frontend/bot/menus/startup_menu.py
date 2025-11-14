from maxapi import Bot, Dispatcher
from maxapi.types import (
    BotStarted,
    Command,
    MessageCreated,
    CallbackButton,
    MessageCallback,
    BotAdded,
    ChatTitleChanged,
    MessageEdited,
    MessageRemoved,
    UserAdded,
    UserRemoved,
    BotStopped,
    DialogCleared,
    DialogMuted,
    DialogUnmuted,
    ChatButton,
    MessageChatCreated
)
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder





def startup_menu():
    builder = InlineKeyboardBuilder()

    builder.row(
        CallbackButton(
            text='Расписание📆',
            payload=str({
                "type": "schedule_list",
                "page": 0
            })
        ),
        CallbackButton(
            text='Настройки⚙',
            payload=str({"type": "settings"}),
        )
    )
    return builder.as_markup()
