from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from texts import TEXTS


def menu(lang):
    return ReplyKeyboardMarkup(
        [
            [TEXTS[lang]["content_ideas"], TEXTS[lang]["captions"]],
            [TEXTS[lang]["hashtags"], TEXTS[lang]["video_script"]],
            [TEXTS[lang]["image_ai"], TEXTS[lang]["video_ai"]],
            [TEXTS[lang]["edit_photo"]],   # زر تعديل الصورة
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


def photo_edit_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["edit_auto"], callback_data="edit_auto")],
        [InlineKeyboardButton(TEXTS[lang]["edit_handsome"], callback_data="edit_handsome")],
        [InlineKeyboardButton(TEXTS[lang]["edit_anime"], callback_data="edit_anime")],
        [InlineKeyboardButton(TEXTS[lang]["edit_cinematic"], callback_data="edit_cinematic")],
        [InlineKeyboardButton(TEXTS[lang]["edit_clothes"], callback_data="edit_clothes")],
        [InlineKeyboardButton(TEXTS[lang]["edit_hair"], callback_data="edit_hair")],
        [InlineKeyboardButton(TEXTS[lang]["edit_beard"], callback_data="edit_beard")],
        [InlineKeyboardButton(TEXTS[lang]["edit_background"], callback_data="edit_background")],
        [InlineKeyboardButton(TEXTS[lang]["edit_lighting"], callback_data="edit_lighting")],
        [InlineKeyboardButton(TEXTS[lang]["edit_colors"], callback_data="edit_colors")],
        [InlineKeyboardButton(TEXTS[lang]["edit_portrait"], callback_data="edit_portrait")],
        [InlineKeyboardButton(TEXTS[lang]["edit_skin"], callback_data="edit_skin")],
        [InlineKeyboardButton(TEXTS[lang]["edit_luxury"], callback_data="edit_luxury")],
        [InlineKeyboardButton(TEXTS[lang]["edit_style"], callback_data="edit_style")],
        [InlineKeyboardButton(TEXTS[lang]["edit_custom"], callback_data="edit_custom")],
    ])