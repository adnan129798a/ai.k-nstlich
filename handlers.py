from telegram import Update
from telegram.ext import ContextTypes

from config import REQUIRED_CHANNEL, REQUIRED_CHANNEL_URL, SUPPORTED_LANGUAGES
from database import (
    create_or_update_user,
    get_user_coins,
    get_user_language,
    set_user_language,
    apply_referral,
    get_referral_count,
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


async def feature_unlocked(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    subscribed = await is_user_subscribed(user_id, context)
    referrals = get_referral_count(user_id)
    return subscribed and referrals >= 3


async def send_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    user = update.effective_user
    if not user:
        return

    username = context.bot.username
    invite_link = f"https://t.me/{username}?start=ref_{user.id}"
    count = get_referral_count(user.id)

    msg = (
        TEXTS[lang]["referral_message"].format(link=invite_link)
        + "\n\n"
        + TEXTS[lang]["your_referral_count"].format(count=count)
    )

    if update.message:
        await update.message.reply_text(msg)
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg)


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

    if context.args:
        first_arg = context.args[0]
        if first_arg.startswith("ref_"):
            try:
                referrer_id = int(first_arg.replace("ref_", ""))
                apply_referral(user.id, referrer_id)
            except Exception:
                pass

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


def generate_content_ideas(topic: str, lang: str) -> str:
    if lang == "ar":
        prompt = f"""
اعطني 5 أفكار فيديوهات قصيرة وقوية لصانع محتوى في مجال:
{topic}

لكل فكرة اكتب:
- الفكرة
- بداية قوية للفيديو
- كابشن
"""
    elif lang == "de":
        prompt = f"Gib mir 5 starke Kurzvideo-Ideen für einen Content Creator im Bereich: {topic}. Für jede Idee: Idee, Hook, Caption."
    elif lang == "tr":
        prompt = f"Bana {topic} alanında içerik üreten biri için 5 güçlü kısa video fikri ver. Her biri için fikir, hook ve caption yaz."
    else:
        prompt = f"Give me 5 strong short video ideas for a content creator in this niche: {topic}. For each idea include the idea, hook, and caption."

    return ask_ai(prompt)


def generate_caption(topic: str, lang: str) -> str:
    if lang == "ar":
        prompt = f"اكتب كابشن احترافي وجذاب لمنشور عن: {topic}"
    elif lang == "de":
        prompt = f"Schreibe eine professionelle und ansprechende Caption über: {topic}"
    elif lang == "tr":
        prompt = f"{topic} hakkında profesyonel ve etkileyici bir caption yaz"
    else:
        prompt = f"Write a professional and engaging caption about: {topic}"

    return ask_ai(prompt)


def generate_hashtags(topic: str, lang: str) -> str:
    if lang == "ar":
        prompt = f"اعطني 10 هاشتاغات قوية ومناسبة لمحتوى عن: {topic}"
    elif lang == "de":
        prompt = f"Gib mir 10 starke und passende Hashtags für Inhalte über: {topic}"
    elif lang == "tr":
        prompt = f"Bana {topic} hakkında içerik için 10 güçlü ve uygun hashtag ver"
    else:
        prompt = f"Give me 10 strong and relevant hashtags for content about: {topic}"

    return ask_ai(prompt)


def generate_script(topic: str, lang: str) -> str:
    if lang == "ar":
        prompt = f"اكتب سكربت فيديو قصير وجذاب عن: {topic} مع بداية قوية ونهاية فيها دعوة للتفاعل."
    elif lang == "de":
        prompt = f"Schreibe ein kurzes, starkes Video-Skript über: {topic} mit starkem Einstieg und Call-to-Action am Ende."
    elif lang == "tr":
        prompt = f"{topic} hakkında güçlü giriş ve etkileşim çağrısı içeren kısa bir video senaryosu yaz."
    else:
        prompt = f"Write a short and engaging video script about: {topic} with a strong hook and a call to action at the end."

    return ask_ai(prompt)


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

    if text == TEXTS[lang]["invite_friends"]:
        await send_referral_info(update, context, lang)
        return

    if text == TEXTS[lang]["my_referrals"]:
        count = get_referral_count(user.id)
        await update.message.reply_text(TEXTS[lang]["your_referral_count"].format(count=count))
        return

    if text == TEXTS[lang]["image_ai"]:
        if not await feature_unlocked(user.id, context):
            await update.message.reply_text(TEXTS[lang]["premium_locked"])
            await send_referral_info(update, context, lang)
            return

        await update.message.reply_text(TEXTS[lang]["premium_unlocked"])
        await update.message.reply_text(TEXTS[lang]["image_coming"])
        return

    if text == TEXTS[lang]["video_ai"]:
        if not await feature_unlocked(user.id, context):
            await update.message.reply_text(TEXTS[lang]["premium_locked"])
            await send_referral_info(update, context, lang)
            return

        await update.message.reply_text(TEXTS[lang]["premium_unlocked"])
        await update.message.reply_text(TEXTS[lang]["video_coming"])
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