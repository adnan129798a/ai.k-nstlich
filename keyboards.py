from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from texts import TEXTS


def menu(lang):
    return ReplyKeyboardMarkup(
        [
            [TEXTS[lang]["content_ideas"], TEXTS[lang]["captions"]],
            [TEXTS[lang]["hashtags"], TEXTS[lang]["video_script"]],
            [TEXTS[lang]["image_ai"], TEXTS[lang]["video_ai"]],
            [TEXTS[lang]["edit_photo"]],
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
        [InlineKeyboardButton(TEXTS[lang]["edit_brighten"], callback_data="edit_brighten")],
        [InlineKeyboardButton(TEXTS[lang]["edit_contrast"], callback_data="edit_contrast")],
        [InlineKeyboardButton(TEXTS[lang]["edit_smooth"], callback_data="edit_smooth")],
        [InlineKeyboardButton(TEXTS[lang]["edit_sharpen"], callback_data="edit_sharpen")],
        [InlineKeyboardButton(TEXTS[lang]["edit_color"], callback_data="edit_color")],
        [InlineKeyboardButton(TEXTS[lang]["edit_formal_suit"], callback_data="edit_formal_suit")],
        [InlineKeyboardButton(TEXTS[lang]["edit_casual_style"], callback_data="edit_casual_style")],
        [InlineKeyboardButton(TEXTS[lang]["edit_luxury_style"], callback_data="edit_luxury_style")],
        [InlineKeyboardButton(TEXTS[lang]["edit_street_style"], callback_data="edit_street_style")],
        [InlineKeyboardButton(TEXTS[lang]["edit_gym_style"], callback_data="edit_gym_style")],
        [InlineKeyboardButton(TEXTS[lang]["edit_arabic_wear"], callback_data="edit_arabic_wear")],
        [InlineKeyboardButton(TEXTS[lang]["edit_black_outfit"], callback_data="edit_black_outfit")],
        [InlineKeyboardButton(TEXTS[lang]["edit_white_outfit"], callback_data="edit_white_outfit")],
        [InlineKeyboardButton(TEXTS[lang]["edit_city_bg"], callback_data="edit_city_bg")],
        [InlineKeyboardButton(TEXTS[lang]["edit_night_bg"], callback_data="edit_night_bg")],
        [InlineKeyboardButton(TEXTS[lang]["edit_studio_bg"], callback_data="edit_studio_bg")],
        [InlineKeyboardButton(TEXTS[lang]["edit_luxury_bg"], callback_data="edit_luxury_bg")],
        [InlineKeyboardButton(TEXTS[lang]["edit_nature_bg"], callback_data="edit_nature_bg")],
        [InlineKeyboardButton(TEXTS[lang]["edit_cafe_bg"], callback_data="edit_cafe_bg")],
        [InlineKeyboardButton(TEXTS[lang]["edit_anime"], callback_data="edit_anime")],
        [InlineKeyboardButton(TEXTS[lang]["edit_cinematic"], callback_data="edit_cinematic")],
        [InlineKeyboardButton(TEXTS[lang]["edit_custom"], callback_data="edit_custom")],
    ])


def video_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["video_free"], callback_data="video_free")],
        [InlineKeyboardButton(TEXTS[lang]["video_singing"], callback_data="video_singing")],
        [InlineKeyboardButton(TEXTS[lang]["video_anime_series"], callback_data="video_anime_series")],
    ])


def video_mode_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["video_mode_realistic"], callback_data="vm_realistic")],
        [InlineKeyboardButton(TEXTS[lang]["video_mode_cinematic"], callback_data="vm_cinematic")],
        [InlineKeyboardButton(TEXTS[lang]["video_mode_anime"], callback_data="vm_anime")],
    ])


def video_length_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["video_len_15"], callback_data="vl_15")],
        [InlineKeyboardButton(TEXTS[lang]["video_len_20"], callback_data="vl_20")],
        [InlineKeyboardButton(TEXTS[lang]["video_len_30"], callback_data="vl_30")],
    ])


def video_ratio_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["video_ratio_916"], callback_data="vr_9_16")],
        [InlineKeyboardButton(TEXTS[lang]["video_ratio_169"], callback_data="vr_16_9")],
        [InlineKeyboardButton(TEXTS[lang]["video_ratio_11"], callback_data="vr_1_1")],
    ])


def video_confirm_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["video_start_now"], callback_data="video_start_now")],
        [InlineKeyboardButton(TEXTS[lang]["video_edit_request"], callback_data="video_edit_request")],
        [InlineKeyboardButton(TEXTS[lang]["video_improve_request"], callback_data="video_improve_request")],
    ])