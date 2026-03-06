from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from texts import TEXTS


def menu(lang):
    return ReplyKeyboardMarkup(
        [
            [TEXTS[lang]["content_ideas"], TEXTS[lang]["captions"]],
            [TEXTS[lang]["hashtags"], TEXTS[lang]["video_script"]],
            [TEXTS[lang]["image_ai"], TEXTS[lang]["video_ai"]],
            [TEXTS[lang]["invite"], TEXTS[lang]["my_ref"]],
        ],
        resize_keyboard=True
    )


def unlock_keyboard(lang, channel_url, invite_link):
    share_url = f"https://t.me/share/url?url={invite_link}&text=🔥 جرب هذا البوت الذكي لصناعة المحتوى"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["join_channel"], url=channel_url)],
        [InlineKeyboardButton(TEXTS[lang]["share_invite"], url=share_url)],
        [InlineKeyboardButton(TEXTS[lang]["check_unlock"], callback_data="check_unlock")]
    ])


def image_style_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["more_realistic"], callback_data="img_hyper_real")],
        [InlineKeyboardButton(TEXTS[lang]["anime_style"], callback_data="img_anime")],
        [InlineKeyboardButton(TEXTS[lang]["cinematic_style"], callback_data="img_cinematic")],
        [InlineKeyboardButton(TEXTS[lang]["regenerate"], callback_data="img_regenerate")]
    ])