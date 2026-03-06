from telegram import Update
from telegram.ext import ContextTypes

from config import REQUIRED_CHANNEL, REQUIRED_CHANNEL_URL, SUPPORTED_LANGUAGES
from database import (
    create_or_update_user,
    get_user_coins,
    get_user_language,
    set_user_language,
)
from keyboards import subscribe_keyboard, main_menu_keyboard, language_keyboard
from texts import TEXTS
from ai_tools import ask_ai


USER_STATES = {}


def detect_language(language_code: str | None) -> str:
    if not language_code:
        return "en"

    short = language_code.split("-")[0].lower()
    return short if short in SUPPORTED_LANGUAGES else "en"


def get_lang(user_id: int, telegram_language_code: str | None = None) -> str:
    saved = get_user_language(user_id)
    if saved in SUPPORTED_LANGUAGES:
        return saved
    return detect_language(telegram_language_code)


async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str) -> bool:
    user = update.effective_user
    if not user:
        return False

    if await is_user_subscribed(user.id, context):
        return True

    text = TEXTS[lang]["subscribe_required"]

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=subscribe_keyboard(lang, REQUIRED_CHANNEL_URL)
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=subscribe_keyboard(lang, REQUIRED_CHANNEL_URL)
        )

    return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message:
        return

    lang = detect_language(user.language_code)

    create_or_update_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language=lang
    )

    if not await require_subscription(update, context, lang):
        return

    await update.message.reply_text(
        f"{TEXTS[lang]['welcome']}\n\n{TEXTS[lang]['main_menu']}",
        reply_markup=main_menu_keyboard(lang)
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    if not query or not user:
        return

    await query.answer()
    lang = get_lang(user.id, user.language_code)

    if await is_user_subscribed(user.id, context):
        await query.message.reply_text(
            TEXTS[lang]["subscription_ok"],
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await query.message.reply_text(
            TEXTS[lang]["subscription_fail"],
            reply_markup=subscribe_keyboard(lang, REQUIRED_CHANNEL_URL)
        )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    if not query or not user:
        return

    await query.answer()
    code = query.data.replace("lang_", "")

    if code not in SUPPORTED_LANGUAGES:
        return

    set_user_language(user.id, code)

    await query.message.reply_text(
        TEXTS[code]["language_changed"],
        reply_markup=main_menu_keyboard(code)
    )


# ---------- AI FUNCTIONS ----------

def generate_content_ideas(topic: str, lang: str) -> str:

    if lang == "ar":
        prompt = f"""
????? 5 ????? ???????? ????? ????? ????? ????? ?? ????:
{topic}

??? ???? ????:
- ??????
- ????? ???? ???????
- ?????
"""

    elif lang == "de":
        prompt = f"Give me 5 strong short video ideas for a content creator in the niche: {topic}"

    elif lang == "tr":
        prompt = f"{topic} alan?nda içerik üreten biri için 5 güçlü k?sa video fikri ver"

    else:
        prompt = f"Give me 5 strong short video ideas for a content creator in the niche: {topic}"

    return ask_ai(prompt)


def generate_caption(topic: str, lang: str) -> str:

    if lang == "ar":
        prompt = f"???? ????? ??????? ????? ?????? ??: {topic}"

    elif lang == "de":
        prompt = f"Write a professional caption about: {topic}"

    elif lang == "tr":
        prompt = f"{topic} hakk?nda etkileyici bir caption yaz"

    else:
        prompt = f"Write a professional caption about: {topic}"

    return ask_ai(prompt)


def generate_hashtags(topic: str, lang: str) -> str:

    if lang == "ar":
        prompt = f"????? 10 ???????? ???? ?????? ??: {topic}"

    else:
        prompt = f"Give me 10 strong hashtags for content about: {topic}"

    return ask_ai(prompt)


def generate_script(topic: str, lang: str) -> str:

    if lang == "ar":
        prompt = f"""
???? ????? ????? ???? ??:
{topic}

????? ????? ?????? ??? ??? ?? ????.
"""

    else:
        prompt = f"Write a short video script about: {topic}"

    return ask_ai(prompt)


# ---------- MESSAGE HANDLER ----------

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not user or not update.message or not update.message.text:
        return

    lang = get_lang(user.id, user.language_code)

    if not await require_subscription(update, context, lang):
        return

    text = update.message.text.strip()

    if text == TEXTS[lang]["content_ideas"]:
        USER_STATES[user.id] = "content_ideas"
        await update.message.reply_text(TEXTS[lang]["ask_topic_content"])
        return

    if text == TEXTS[lang]["captions"]:
        USER_STATES[user.id] = "captions"
        await update.message.reply_text(TEXTS[lang]["ask_topic_caption"])
        return

    if text == TEXTS[lang]["hashtags"]:
        USER_STATES[user.id] = "hashtags"
        await update.message.reply_text(TEXTS[lang]["ask_topic_hashtags"])
        return

    if text == TEXTS[lang]["video_script"]:
        USER_STATES[user.id] = "video_script"
        await update.message.reply_text(TEXTS[lang]["ask_topic_script"])
        return

    if text == TEXTS[lang]["coins"]:
        coins = get_user_coins(user.id)
        await update.message.reply_text(TEXTS[lang]["your_coins"].format(coins=coins))
        return

    if text == TEXTS[lang]["language"]:
        await update.message.reply_text(
            TEXTS[lang]["choose_language"],
            reply_markup=language_keyboard()
        )
        return

    state = USER_STATES.get(user.id)

    if state == "content_ideas":
        result = generate_content_ideas(text, lang)
        await update.message.reply_text(result)
        USER_STATES.pop(user.id, None)
        return

    if state == "captions":
        result = generate_caption(text, lang)
        await update.message.reply_text(result)
        USER_STATES.pop(user.id, None)
        return

    if state == "hashtags":
        result = generate_hashtags(text, lang)
        await update.message.reply_text(result)
        USER_STATES.pop(user.id, None)
        return

    if state == "video_script":
        result = generate_script(text, lang)
        await update.message.reply_text(result)
        USER_STATES.pop(user.id, None)
        return

    await update.message.reply_text(TEXTS[lang]["not_understood"])