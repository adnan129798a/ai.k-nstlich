from io import BytesIO

from telegram import Update
from telegram.ext import ContextTypes

from database import add_user, set_referral, get_referrals
from texts import TEXTS
from keyboards import (
    menu,
    unlock_keyboard,
    image_style_keyboard,
    photo_edit_keyboard,
    video_menu_keyboard,
    video_mode_keyboard,
    video_length_keyboard,
    video_ratio_keyboard,
    video_confirm_keyboard,
)
from config import REQUIRED_CHANNEL, REQUIRED_CHANNEL_URL
from ai_tools import ask_ai
from image_tools import generate_image_bytes, edit_image_bytes
from photo_enhance import (
    auto_enhance,
    brighten,
    contrast,
    smooth,
    sharpen,
    color_boost,
    custom_edit,
)
from video_tools import create_video_job, wait_for_video, download_video_bytes

LANG = "ar"
USER_STATES = {}
LAST_IMAGE_PROMPTS = {}
LAST_USER_PHOTOS = {}
VIDEO_DRAFTS = {}


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
لكل فكرة:
- عنوان
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
"""


def strong_preserve_instruction(extra: str) -> str:
    return (
        "Preserve the exact same person, same identity, same facial features, same face shape, "
        "same eyes, same nose, same mouth, same beard, same hairstyle, same body pose, same camera angle. "
        "Do not change the person's identity or face. Only apply the requested change to clothes, background, "
        "mood, or artistic style. "
        + extra
    )


def preset_instruction_map():
    return {
        "edit_formal_suit": strong_preserve_instruction(
            "Change only the outfit into a luxurious black formal suit."
        ),
        "edit_casual_style": strong_preserve_instruction(
            "Change only the outfit into a stylish casual modern look."
        ),
        "edit_luxury_style": strong_preserve_instruction(
            "Make the image luxurious with elegant outfit and classy atmosphere."
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
            "Change only the clothes into a stylish black outfit."
        ),
        "edit_white_outfit": strong_preserve_instruction(
            "Change only the clothes into a stylish white outfit."
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
            "same facial structure, same hairstyle, same pose, and keep the face as close as possible."
        ),
    }


def _video_defaults(user_id: int):
    VIDEO_DRAFTS.setdefault(
        user_id,
        {
            "kind": None,
            "idea": "",
            "mode": "",
            "seconds": 15,
            "ratio": "9:16",
            "people": "",
            "action_type": "",
            "mood": "",
            "music": "",
            "singing_type": "",
            "voice": "",
            "place": "",
            "lyrics": "",
            "performance_style": "",
            "story": "",
            "genre": "",
            "anime_style": "",
            "characters": "",
            "narrator": "",
        },
    )


def build_video_summary(data: dict) -> str:
    lines = [TEXTS[LANG]["video_summary"], ""]

    if data["kind"] == "free":
        lines += [
            "النوع: فيديو حر",
            f"الفكرة: {data['idea']}",
            f"النمط: {data['mode']}",
            f"المدة: {data['seconds']} ثانية",
            f"المقاس: {data['ratio']}",
            f"الشخصيات: {data['people']}",
            f"الحركة/الكلام: {data['action_type']}",
            f"الجو: {data['mood']}",
            f"الصوت: {data['music']}",
        ]

    elif data["kind"] == "singing":
        lines += [
            "النوع: غناء / قصيدة / أداء",
            f"الأسلوب: {data['singing_type']}",
            f"الصوت: {data['voice']}",
            f"المكان: {data['place']}",
            f"النمط: {data['mode']}",
            f"المدة: {data['seconds']} ثانية",
            f"المقاس: {data['ratio']}",
            f"الكلمات/النص: {data['lyrics']}",
            f"الأداء: {data['performance_style']}",
        ]

    elif data["kind"] == "series":
        lines += [
            "النوع: مسلسل أنيمي",
            f"القصة: {data['story']}",
            f"التصنيف: {data['genre']}",
            f"الستايل: {data['anime_style']}",
            f"عدد الشخصيات: {data['characters']}",
            f"الراوي: {data['narrator']}",
            f"المدة: {data['seconds']} ثانية",
            f"المقاس: {data['ratio']}",
        ]

    return "\n".join(lines)


def improve_video_summary(summary: str) -> str:
    prompt = f"""
حسّن هذا الطلب لفيديو ذكاء اصطناعي ليصبح أقوى وأكثر احترافية
لكن بدون تغيير فكرته الأساسية.

الطلب:
{summary}

أعد كتابته بشكل أفضل ومرتب وواضح.
"""
    return ask_ai(prompt)


def build_video_generation_prompt(data: dict) -> str:
    if data["kind"] == "free":
        return (
            f"Create a {data['mode']} video about: {data['idea']}. "
            f"Duration: {data['seconds']} seconds. Aspect ratio: {data['ratio']}. "
            f"Characters: {data['people']}. "
            f"Action/dialogue style: {data['action_type']}. "
            f"Mood: {data['mood']}. "
            f"Audio preference: {data['music']}. "
            f"Make it visually strong, social-media ready, detailed, cinematic, smooth motion."
        )

    if data["kind"] == "singing":
        lyrics = data["lyrics"]
        if lyrics.strip() == "اقترح":
            lyrics = "Original artistic vocal performance with emotionally fitting words."
        return (
            f"Create a {data['mode']} performance video. "
            f"Type: {data['singing_type']}. Voice: {data['voice']}. "
            f"Location: {data['place']}. Duration: {data['seconds']} seconds. "
            f"Aspect ratio: {data['ratio']}. "
            f"Lyrics/text: {lyrics}. "
            f"Performance style: {data['performance_style']}. "
            f"Make it expressive, emotional, polished, and social-media ready."
        )

    if data["kind"] == "series":
        story = data["story"]
        if story.strip() == "اقترح":
            story = ask_ai(
                f"اقترح لي قصة قصيرة جدًا لمسلسل أنيمي من نوع {data['genre']} "
                f"بستايل {data['anime_style']} مع {data['characters']} شخصيات رئيسية."
            )

        return (
            f"Create episode 1 of an anime mini-series. "
            f"Story: {story}. Genre: {data['genre']}. "
            f"Anime style: {data['anime_style']}. "
            f"Main characters count: {data['characters']}. "
            f"Narrator: {data['narrator']}. "
            f"Duration: {data['seconds']} seconds. Aspect ratio: {data['ratio']}. "
            f"Make it coherent, visually attractive, episode-like, and social-media friendly."
        )

    return "Create a short cinematic video."


async def send_generated_image(chat_id: int, prompt: str, style: str, context: ContextTypes.DEFAULT_TYPE):
    image_bytes = generate_image_bytes(prompt, style=style)

    bio = BytesIO(image_bytes)
    bio.name = "generated.png"
    bio.seek(0)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=bio,
        caption=TEXTS[LANG]["image_generated"],
        reply_markup=image_style_keyboard(LANG),
    )


async def send_edited_photo(chat_id: int, image_bytes: bytes, context: ContextTypes.DEFAULT_TYPE):
    bio = BytesIO(image_bytes)
    bio.name = "edited.jpg"
    bio.seek(0)
    await context.bot.send_photo(chat_id=chat_id, photo=bio, caption=TEXTS[LANG]["edit_done"])


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

    await update.message.reply_text(TEXTS[LANG]["welcome"], reply_markup=menu(LANG))


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
                reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link),
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
                reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link),
            )
        else:
            _video_defaults(user.id)
            await update.message.reply_text(
                TEXTS[LANG]["video_menu_intro"],
                reply_markup=video_menu_keyboard(LANG),
            )
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

    # video states
    data = VIDEO_DRAFTS.get(user.id)
    if not data:
        return

    if state == "video_free_idea":
        data["idea"] = msg
        USER_STATES[user.id] = "video_choose_mode"
        await update.message.reply_text(
            TEXTS[LANG]["video_choose_mode"],
            reply_markup=video_mode_keyboard(LANG),
        )
        return

    if state == "video_free_people":
        data["people"] = msg
        USER_STATES[user.id] = "video_free_action"
        await update.message.reply_text(TEXTS[LANG]["video_free_action"])
        return

    if state == "video_free_action":
        data["action_type"] = msg
        USER_STATES[user.id] = "video_free_mood"
        await update.message.reply_text(TEXTS[LANG]["video_free_mood"])
        return

    if state == "video_free_mood":
        data["mood"] = msg
        USER_STATES[user.id] = "video_free_music"
        await update.message.reply_text(TEXTS[LANG]["video_free_music"])
        return

    if state == "video_free_music":
        data["music"] = msg
        summary = build_video_summary(data)
        USER_STATES[user.id] = "video_confirm"
        await update.message.reply_text(summary, reply_markup=video_confirm_keyboard(LANG))
        return

    if state == "video_singing_type":
        data["singing_type"] = msg
        USER_STATES[user.id] = "video_choose_mode"
        await update.message.reply_text(
            TEXTS[LANG]["video_choose_mode"],
            reply_markup=video_mode_keyboard(LANG),
        )
        return

    if state == "video_singing_voice":
        data["voice"] = msg
        USER_STATES[user.id] = "video_singing_place"
        await update.message.reply_text(TEXTS[LANG]["video_singing_place"])
        return

    if state == "video_singing_place":
        data["place"] = msg
        USER_STATES[user.id] = "video_singing_words"
        await update.message.reply_text(TEXTS[LANG]["video_singing_words"])
        return

    if state == "video_singing_words":
        data["lyrics"] = msg
        USER_STATES[user.id] = "video_singing_style"
        await update.message.reply_text(TEXTS[LANG]["video_singing_style"])
        return

    if state == "video_singing_style":
        data["performance_style"] = msg
        summary = build_video_summary(data)
        USER_STATES[user.id] = "video_confirm"
        await update.message.reply_text(summary, reply_markup=video_confirm_keyboard(LANG))
        return

    if state == "video_series_story":
        data["story"] = msg
        USER_STATES[user.id] = "video_choose_length"
        await update.message.reply_text(
            TEXTS[LANG]["video_choose_length"],
            reply_markup=video_length_keyboard(LANG),
        )
        return

    if state == "video_series_genre":
        data["genre"] = msg
        USER_STATES[user.id] = "video_series_style"
        await update.message.reply_text(TEXTS[LANG]["video_series_style"])
        return

    if state == "video_series_style":
        data["anime_style"] = msg
        USER_STATES[user.id] = "video_series_chars"
        await update.message.reply_text(TEXTS[LANG]["video_series_chars"])
        return

    if state == "video_series_chars":
        data["characters"] = msg
        USER_STATES[user.id] = "video_series_narrator"
        await update.message.reply_text(TEXTS[LANG]["video_series_narrator"])
        return

    if state == "video_series_narrator":
        data["narrator"] = msg
        summary = build_video_summary(data)
        USER_STATES[user.id] = "video_confirm"
        await update.message.reply_text(summary, reply_markup=video_confirm_keyboard(LANG))
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
        reply_markup=photo_edit_keyboard(LANG),
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
            reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link),
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


async def video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user

    if not query or not user:
        return

    await query.answer()
    code = query.data

    _video_defaults(user.id)
    data = VIDEO_DRAFTS[user.id]

    if code == "video_free":
        data["kind"] = "free"
        USER_STATES[user.id] = "video_free_idea"
        await query.message.reply_text(TEXTS[LANG]["video_free_idea"])
        return

    if code == "video_singing":
        data["kind"] = "singing"
        USER_STATES[user.id] = "video_singing_type"
        await query.message.reply_text(TEXTS[LANG]["video_singing_type"])
        return

    if code == "video_anime_series":
        data["kind"] = "series"
        USER_STATES[user.id] = "video_series_story"
        await query.message.reply_text(TEXTS[LANG]["video_series_story"])
        return

    if code.startswith("vm_"):
        mode_map = {
            "vm_realistic": "واقعي",
            "vm_cinematic": "سينمائي",
            "vm_anime": "أنيمي",
        }
        data["mode"] = mode_map.get(code, "واقعي")
        USER_STATES[user.id] = "video_choose_length"
        await query.message.reply_text(
            TEXTS[LANG]["video_choose_length"],
            reply_markup=video_length_keyboard(LANG),
        )
        return

    if code.startswith("vl_"):
        sec_map = {
            "vl_15": 15,
            "vl_20": 20,
            "vl_30": 30,
        }
        data["seconds"] = sec_map.get(code, 15)
        USER_STATES[user.id] = "video_choose_ratio"
        await query.message.reply_text(
            TEXTS[LANG]["video_choose_ratio"],
            reply_markup=video_ratio_keyboard(LANG),
        )
        return

    if code.startswith("vr_"):
        ratio_map = {
            "vr_9_16": "9:16",
            "vr_16_9": "16:9",
            "vr_1_1": "1:1",
        }
        data["ratio"] = ratio_map.get(code, "9:16")

        if data["kind"] == "free":
            USER_STATES[user.id] = "video_free_people"
            await query.message.reply_text(TEXTS[LANG]["video_free_people"])
            return

        if data["kind"] == "singing":
            USER_STATES[user.id] = "video_singing_voice"
            await query.message.reply_text(TEXTS[LANG]["video_singing_voice"])
            return

        if data["kind"] == "series":
            USER_STATES[user.id] = "video_series_genre"
            await query.message.reply_text(TEXTS[LANG]["video_series_genre"])
            return

    if code == "video_start_now":
        USER_STATES.pop(user.id, None)
        prompt = build_video_generation_prompt(data)
        await query.message.reply_text(TEXTS[LANG]["video_generating"])

        try:
            job = create_video_job(
                prompt=prompt,
                seconds=data["seconds"],
                aspect_ratio=data["ratio"],
            )
            video_id = job.get("id")

            if not video_id:
                await query.message.reply_text(TEXTS[LANG]["video_generation_failed"])
                return

            await wait_for_video(video_id)
            video_bytes = download_video_bytes(video_id)

            bio = BytesIO(video_bytes)
            bio.name = "generated_video.mp4"
            bio.seek(0)

            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=bio,
                caption=TEXTS[LANG]["video_ready"],
            )
        except Exception as e:
            await query.message.reply_text(f"{TEXTS[LANG]['video_generation_failed']}\n{str(e)}")
        return

    if code == "video_edit_request":
        kind = data.get("kind")

        if kind == "free":
            USER_STATES[user.id] = "video_free_idea"
            await query.message.reply_text("أعد كتابة فكرة الفيديو من جديد.")
            return

        if kind == "singing":
            USER_STATES[user.id] = "video_singing_type"
            await query.message.reply_text(TEXTS[LANG]["video_singing_type"])
            return

        if kind == "series":
            USER_STATES[user.id] = "video_series_story"
            await query.message.reply_text(TEXTS[LANG]["video_series_story"])
            return

    if code == "video_improve_request":
        summary = build_video_summary(data)
        improved = improve_video_summary(summary)
        await query.message.reply_text(f"{TEXTS[LANG]['video_improved_summary']}\n\n{improved}")
        await query.message.reply_text(
            build_video_summary(data),
            reply_markup=video_confirm_keyboard(LANG),
        )