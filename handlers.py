from io import BytesIO

from telegram import Update
from telegram.ext import ContextTypes

from database import add_user, set_referral, get_referrals
from texts import TEXTS
from keyboards import menu, unlock_keyboard, image_style_keyboard, photo_edit_keyboard
from config import REQUIRED_CHANNEL, REQUIRED_CHANNEL_URL
from ai_tools import ask_ai
from image_tools import generate_image_bytes, edit_image_bytes
from photo_enhance import auto_enhance, brighten, contrast, smooth, sharpen, color_boost, custom_edit

LANG = "ar"
USER_STATES = {}
LAST_IMAGE_PROMPTS = {}
LAST_USER_PHOTOS = {}


def get_invite_link(bot_username, user_id):
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


def content_ideas_prompt(topic: str) -> str:
    return f"""
اعطني 5 أفكار محتوى احترافية عن: {topic}

لكل فكرة اكتب:
- عنوان الفكرة
- Hook قوي
- CTA قصير
واجعلها مناسبة لريلز وتيك توك.
"""


def captions_prompt(topic: str) -> str:
    return f"""
اكتب لي 3 كابشنات احترافية وجذابة عن: {topic}
واجعلها قصيرة ومناسبة للسوشال ميديا.
"""


def hashtags_prompt(topic: str) -> str:
    return f"""
اعطني 15 هاشتاغ مناسب لمحتوى عن: {topic}
واجعلها مزيج عربي وإنجليزي.
"""


def script_prompt(topic: str) -> str:
    return f"""
اكتب سكربت فيديو قصير واحترافي عن: {topic}

الشكل:
- Hook
- Body
- CTA
ويكون مناسب لفيديو قصير.
"""


def video_prompt(topic: str) -> str:
    return f"""
اكتب وصف فيديو احترافي جاهز للتوليد بالذكاء الاصطناعي عن: {topic}

اكتب:
- prompt إنجليزي قوي
- نوع اللقطات
- حركة الكاميرا
- الإضاءة
- الجو العام
- المقاس المناسب للسوشال ميديا 9:16
"""


def strong_preserve_instruction(extra: str) -> str:
    return (
        "Preserve the exact same person, same identity, same facial features, same face shape, "
        "same eyes, same nose, same mouth, same beard, same hairstyle, same body pose, same phone, "
        "same camera angle. Do not change the person's identity or face. "
        "Only apply the requested change to clothes, background, mood, or artistic style. "
        + extra
    )


def preset_instruction_map():
    return {
        "edit_formal_suit": strong_preserve_instruction(
            "Change only the outfit into a luxurious black formal suit with elegant details."
        ),
        "edit_casual_style": strong_preserve_instruction(
            "Change only the outfit into a stylish casual modern look."
        ),
        "edit_luxury_style": strong_preserve_instruction(
            "Make the overall image luxurious and premium, with elegant outfit and classy atmosphere."
        ),
        "edit_street_style": strong_preserve_instruction(
            "Change only the clothes into fashionable streetwear."
        ),
        "edit_gym_style": strong_preserve_instruction(
            "Change only the clothes into premium athletic gym wear."
        ),
        "edit_arabic_wear": strong_preserve_instruction(
            "Change only the outfit into elegant Arabic traditional wear."
        ),
        "edit_black_outfit": strong_preserve_instruction(
            "Change only the clothes into a clean stylish black outfit."
        ),
        "edit_white_outfit": strong_preserve_instruction(
            "Change only the clothes into a clean stylish white outfit."
        ),
        "edit_city_bg": strong_preserve_instruction(
            "Keep the same person and outfit, change only the background to a modern city."
        ),
        "edit_night_bg": strong_preserve_instruction(
            "Keep the same person and outfit, change only the background to a cinematic night city."
        ),
        "edit_studio_bg": strong_preserve_instruction(
            "Keep the same person and outfit, change only the background to a professional studio."
        ),
        "edit_luxury_bg": strong_preserve_instruction(
            "Keep the same person and outfit, change only the background to a luxurious interior."
        ),
        "edit_nature_bg": strong_preserve_instruction(
            "Keep the same person and outfit, change only the background to elegant nature."
        ),
        "edit_cafe_bg": strong_preserve_instruction(
            "Keep the same person and outfit, change only the background to a stylish cafe."
        ),
        "edit_cinematic": strong_preserve_instruction(
            "Keep the same person. Add cinematic lighting and cinematic color grading."
        ),
        "edit_anime": (
            "Transform this image into anime style while preserving the same person, same identity, "
            "same facial structure, same hairstyle, same pose, and make the face as close as possible."
        ),
    }


async def send_generated_image(chat_id: int, prompt: str, style: str, context: ContextTypes.DEFAULT_TYPE):
    image_bytes = generate_image_bytes(prompt, style=style)

    bio = BytesIO(image_bytes)
    bio.name = "generated.png"
    bio.seek(0)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=bio,
        caption=TEXTS[LANG]["image_generated"],
        reply_markup=image_style_keyboard(LANG)
    )


async def send_edited_photo(chat_id: int, image_bytes: bytes, context: ContextTypes.DEFAULT_TYPE):
    bio = BytesIO(image_bytes)
    bio.name = "edited.jpg"
    bio.seek(0)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=bio,
        caption=TEXTS[LANG]["edit_done"]
    )


async def get_user_photo_bytes(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> bytes:
    tg_file = await context.bot.get_file(file_id)
    data = await tg_file.download_as_bytearray()
    return bytes(data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return

    add_user(user.id, user.username)

    if context.args:
        ref = context.args[0]
        if ref.startswith("ref_"):
            try:
                referrer = int(ref.replace("ref_", ""))
                if referrer != user.id:
                    set_referral(user.id, referrer)
            except Exception:
                pass

    await update.message.reply_text(
        TEXTS[LANG]["welcome"],
        reply_markup=menu(LANG)
    )


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return

    msg = update.message.text.strip()
    invite_link = get_invite_link(context.bot.username, user.id)

    if msg == TEXTS[LANG]["content_ideas"]:
        USER_STATES[user.id] = "content_ideas"
        await update.message.reply_text(TEXTS[LANG]["ask_content"])
        return

    if msg == TEXTS[LANG]["captions"]:
        USER_STATES[user.id] = "captions"
        await update.message.reply_text(TEXTS[LANG]["ask_caption"])
        return

    if msg == TEXTS[LANG]["hashtags"]:
        USER_STATES[user.id] = "hashtags"
        await update.message.reply_text(TEXTS[LANG]["ask_hashtags"])
        return

    if msg == TEXTS[LANG]["video_script"]:
        USER_STATES[user.id] = "video_script"
        await update.message.reply_text(TEXTS[LANG]["ask_script"])
        return

    if msg == TEXTS[LANG]["invite"]:
        await update.message.reply_text(TEXTS[LANG]["invite_text"].format(link=invite_link))
        return

    if msg == TEXTS[LANG]["my_ref"]:
        count = get_referrals(user.id)
        await update.message.reply_text(TEXTS[LANG]["ref_count"].format(count=count))
        return

    if msg == TEXTS[LANG]["edit_photo"]:
        USER_STATES[user.id] = "waiting_edit_photo"
        await update.message.reply_text(TEXTS[LANG]["send_photo_to_edit"])
        return

    if msg == TEXTS[LANG]["image_ai"]:
        refs = get_referrals(user.id)
        subscribed = await is_subscribed(user.id, context)

        if refs < 1 or not subscribed:
            await update.message.reply_text(
                TEXTS[LANG]["locked"],
                reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link)
            )
        else:
            USER_STATES[user.id] = "image_ai"
            await update.message.reply_text(TEXTS[LANG]["image_ok"])
            await update.message.reply_text(TEXTS[LANG]["ask_image"])
        return

    if msg == TEXTS[LANG]["video_ai"]:
        refs = get_referrals(user.id)
        subscribed = await is_subscribed(user.id, context)

        if refs < 1 or not subscribed:
            await update.message.reply_text(
                TEXTS[LANG]["locked"],
                reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link)
            )
        else:
            USER_STATES[user.id] = "video_ai"
            await update.message.reply_text(TEXTS[LANG]["video_ok"])
            await update.message.reply_text(TEXTS[LANG]["ask_video"])
        return

    state = USER_STATES.get(user.id)

    if state == "content_ideas":
        USER_STATES.pop(user.id, None)
        await update.message.reply_text(ask_ai(content_ideas_prompt(msg)))
        return

    if state == "captions":
        USER_STATES.pop(user.id, None)
        await update.message.reply_text(ask_ai(captions_prompt(msg)))
        return

    if state == "hashtags":
        USER_STATES.pop(user.id, None)
        await update.message.reply_text(ask_ai(hashtags_prompt(msg)))
        return

    if state == "video_script":
        USER_STATES.pop(user.id, None)
        await update.message.reply_text(ask_ai(script_prompt(msg)))
        return

    if state == "image_ai":
        USER_STATES.pop(user.id, None)
        LAST_IMAGE_PROMPTS[user.id] = msg
        await update.message.reply_text(TEXTS[LANG]["image_generating"])

        try:
            await send_generated_image(update.effective_chat.id, msg, "realistic", context)
        except Exception as e:
            await update.message.reply_text(f"{TEXTS[LANG]['image_failed']}\n{str(e)}")
        return

    if state == "video_ai":
        USER_STATES.pop(user.id, None)
        await update.message.reply_text(TEXTS[LANG]["video_generating"])
        try:
            await update.message.reply_text(ask_ai(video_prompt(msg)))
        except Exception as e:
            await update.message.reply_text(f"{TEXTS[LANG]['video_failed']}\n{str(e)}")
        return

    if state == "waiting_custom_edit_instruction":
        USER_STATES.pop(user.id, None)

        file_id = LAST_USER_PHOTOS.get(user.id)
        if not file_id:
            await update.message.reply_text(TEXTS[LANG]["please_send_photo_first"])
            return

        await update.message.reply_text(TEXTS[LANG]["edit_note_preserve"])
        await update.message.reply_text(TEXTS[LANG]["edit_generating"])

        try:
            original = await get_user_photo_bytes(file_id, context)
            instruction = strong_preserve_instruction(msg)
            edited = edit_image_bytes(original, instruction)
            await send_edited_photo(update.effective_chat.id, edited, context)
        except Exception as e:
            await update.message.reply_text(f"{TEXTS[LANG]['edit_failed']}\n{str(e)}")
        return


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message or not update.message.photo:
        return

    state = USER_STATES.get(user.id)

    if state != "waiting_edit_photo":
        return

    photo = update.message.photo[-1]
    LAST_USER_PHOTOS[user.id] = photo.file_id
    USER_STATES.pop(user.id, None)

    await update.message.reply_text(
        TEXTS[LANG]["photo_received"],
        reply_markup=photo_edit_keyboard(LANG)
    )


async def check_unlock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user

    if not query or not user:
        return

    await query.answer()

    refs = get_referrals(user.id)
    subscribed = await is_subscribed(user.id, context)
    invite_link = get_invite_link(context.bot.username, user.id)

    if refs >= 1 and subscribed:
        await query.message.reply_text(TEXTS[LANG]["unlocked_now"])
    else:
        await query.message.reply_text(
            TEXTS[LANG]["still_locked"],
            reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link)
        )


async def image_style_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user

    if not query or not user:
        return

    await query.answer()

    prompt = LAST_IMAGE_PROMPTS.get(user.id)
    if not prompt:
        await query.message.reply_text("اكتب وصف صورة جديد أولًا.")
        return

    style_map = {
        "img_hyper_real": "hyper_real",
        "img_anime": "anime",
        "img_cinematic": "cinematic",
        "img_regenerate": "realistic",
    }

    style = style_map.get(query.data, "realistic")

    await query.message.reply_text(TEXTS[LANG]["image_generating"])

    try:
        await send_generated_image(query.message.chat_id, prompt, style, context)
    except Exception as e:
        await query.message.reply_text(f"{TEXTS[LANG]['image_failed']}\n{str(e)}")


async def photo_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user

    if not query or not user:
        return

    await query.answer()

    file_id = LAST_USER_PHOTOS.get(user.id)
    if not file_id:
        await query.message.reply_text(TEXTS[LANG]["please_send_photo_first"])
        return

    data = query.data

    if data == "edit_custom":
        USER_STATES[user.id] = "waiting_custom_edit_instruction"
        await query.message.reply_text(TEXTS[LANG]["edit_custom_prompt"])
        return

    await query.message.reply_text(TEXTS[LANG]["edit_generating"])

    try:
        original = await get_user_photo_bytes(file_id, context)

        if data == "edit_auto":
            edited = auto_enhance(original)
        elif data == "edit_brighten":
            edited = brighten(original)
        elif data == "edit_contrast":
            edited = contrast(original)
        elif data == "edit_smooth":
            edited = smooth(original)
        elif data == "edit_sharpen":
            edited = sharpen(original)
        elif data == "edit_color":
            edited = color_boost(original)
        else:
            instruction = preset_instruction_map().get(data)
            if not instruction:
                await query.message.reply_text(TEXTS[LANG]["edit_failed"])
                return
            await query.message.reply_text(TEXTS[LANG]["edit_note_preserve"])
            edited = edit_image_bytes(original, instruction)

        await send_edited_photo(query.message.chat_id, edited, context)
    except Exception as e:
        await query.message.reply_text(f"{TEXTS[LANG]['edit_failed']}\n{str(e)}")