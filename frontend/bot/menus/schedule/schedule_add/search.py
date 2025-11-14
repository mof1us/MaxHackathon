from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton


def search_results_display(builder: InlineKeyboardBuilder, search_results_entries: list[tuple[str, str]]):
    for sre in search_results_entries:
        builder.row(CallbackButton(text=sre[0], payload=str({
            "type": "search_result",
            "result_payload": sre[1]
        })))