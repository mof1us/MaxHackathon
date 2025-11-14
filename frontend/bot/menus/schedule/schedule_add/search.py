from data_types.University import University
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton


def search_results_display(builder: InlineKeyboardBuilder, search_results_entries: list[University]):
    for sre in search_results_entries:
        builder.row(CallbackButton(text=sre.name, payload=str({
            "type": "search_result",
            "result_payload": str(sre.id)
        })))