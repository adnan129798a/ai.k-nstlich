from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from texts import TEXTS


def subscribe_keyboard(lang: str, channel_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["join_channel"], url=channel_url)],
        [InlineKeyboardButton(TEXTS[lang]["check_subscription"], callback_data="check_subscription")]
    ])


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [TEXTS[lang]["content_ideas"], TEXTS[lang]["captions"]],
            [TEXTS[lang]["hashtags"], TEXTS[lang]["video_script"]],
            [TEXTS[lang]["image_ai"], TEXTS[lang]["video_ai"]],
            [TEXTS[lang]["invite_friends"], TEXTS[lang]["my_referrals"]],
            [TEXTS[lang]["coins"], TEXTS[lang]["language"]],
        ],
        resize_keyboard=True
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("Türkçe", callback_data="lang_tr")],
    ])