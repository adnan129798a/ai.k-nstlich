from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from texts import TEXTS


def menu(lang):
    return ReplyKeyboardMarkup(
        [
            [TEXTS[lang]["content_ideas"], TEXTS[lang]["captions"]],
            [TEXTS[lang]["hashtags"], TEXTS[lang]["video_script"]],
            [TEXTS[lang]["image_ai"], TEXTS[lang]["video_ai"]],
            [TEXTS[lang]["invite"], TEXTS[lang]["my_ref"]]
        ],
        resize_keyboard=True
    )


def unlock_keyboard(lang, channel_url, invite_link):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["join_channel"], url=channel_url)],
        [InlineKeyboardButton(TEXTS[lang]["share_invite"], url=invite_link)],
        [InlineKeyboardButton(TEXTS[lang]["check_unlock"], callback_data="check_unlock")]
    ])