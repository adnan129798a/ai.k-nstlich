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


def generate_content_ideas(topic: str, lang: str) -> str:
    if lang == "ar":
        return (
            f"1. فيديو: 3 أخطاء شائعة في {topic}\n"
            f"2. فيديو: قبل وبعد في {topic}\n"
            f"3. فيديو: يوم في حياة شخص يعمل في {topic}\n"
            f"4. فيديو: أفضل 5 أفكار تخص {topic}\n"
            f"5. فيديو: أسرار النجاح في {topic}"
        )
    if lang == "de":
        return (
            f"1. Video: 3 häufige Fehler in {topic}\n"
            f"2. Video: Vorher/Nachher in {topic}\n"
            f"3. Video: Ein Tag im Leben in {topic}\n"
            f"4. Video: 5 starke Ideen für {topic}\n"
            f"5. Video: Erfolgsgeheimnisse in {topic}"
        )
    if lang == "tr":
        return (
            f"1. Video: {topic} alanında 3 yaygın hata\n"
            f"2. Video: {topic} için önce/sonra fikri\n"
            f"3. Video: {topic} ile ilgili bir günüm\n"
            f"4. Video: {topic} hakkında 5 güçlü fikir\n"
            f"5. Video: {topic} başarısının sırları"
        )
    return (
        f"1. Video: 3 common mistakes in {topic}\n"
        f"2. Video: Before/after in {topic}\n"
        f"3. Video: A day in the life in {topic}\n"
        f"4. Video: 5 strong ideas about {topic}\n"
        f"5. Video: Secrets of success in {topic}"
    )


def generate_caption(topic: str, lang: str) -> str:
    if lang == "ar":
        return f"إذا كنت تحب {topic} فهذا المحتوى لك 🔥 تابع للنهاية ولا تنسَ رأيك."
    if lang == "de":
        return f"Wenn du {topic} liebst, ist dieser Inhalt genau für dich 🔥 Bleib bis zum Ende dran."
    if lang == "tr":
        return f"{topic} seviyorsan bu içerik tam sana göre 🔥 Sonuna kadar izle ve fikrini yaz."
    return f"If you love {topic}, this content is for you 🔥 Watch till the end and share your opinion."


def generate_hashtags(topic: str, lang: str) -> str:
    cleaned = topic.replace(" ", "")
    return f"#{cleaned} #viral #fyp #content #reels #tiktok"


def generate_script(topic: str, lang: str) -> str:
    if lang == "ar":
        return (
            f"المشهد 1: مقدمة سريعة عن {topic}\n"
            f"المشهد 2: عرض أهم نقطة بشكل جذاب\n"
            f"المشهد 3: مثال أو نتيجة واضحة\n"
            f"المشهد 4: دعوة للتفاعل والمتابعة"
        )
    if lang == "de":
        return (
            f"Szene 1: Kurze Einführung zu {topic}\n"
            f"Szene 2: Wichtigsten Punkt spannend zeigen\n"
            f"Szene 3: Beispiel oder klares Ergebnis\n"
            f"Szene 4: Call-to-Action für Interaktion"
        )
    if lang == "tr":
        return (
            f"Sahne 1: {topic} hakkında hızlı giriş\n"
            f"Sahne 2: En önemli noktayı etkileyici göster\n"
            f"Sahne 3: Örnek veya net sonuç ver\n"
            f"Sahne 4: Etkileşim çağrısı yap"
        )
    return (
        f"Scene 1: Quick intro about {topic}\n"
        f"Scene 2: Show the most important point in an engaging way\n"
        f"Scene 3: Give an example or clear result\n"
        f"Scene 4: Add a call to action"
    )


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
        await update.message.reply_text(f"{TEXTS[lang]['result_title']}\n\n{result}")
        USER_STATES.pop(user.id, None)
        return

    if state == "captions":
        result = generate_caption(text, lang)
        await update.message.reply_text(f"{TEXTS[lang]['result_title']}\n\n{result}")
        USER_STATES.pop(user.id, None)
        return

    if state == "hashtags":
        result = generate_hashtags(text, lang)
        await update.message.reply_text(f"{TEXTS[lang]['result_title']}\n\n{result}")
        USER_STATES.pop(user.id, None)
        return

    if state == "video_script":
        result = generate_script(text, lang)
        await update.message.reply_text(f"{TEXTS[lang]['result_title']}\n\n{result}")
        USER_STATES.pop(user.id, None)
        return

    await update.message.reply_text(TEXTS[lang]["not_understood"])