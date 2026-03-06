from telegram import Update
from telegram.ext import ContextTypes

from database import add_user, set_referral, get_referrals
from texts import TEXTS
from keyboards import menu, unlock_keyboard
from config import REQUIRED_CHANNEL, REQUIRED_CHANNEL_URL

LANG = "ar"
USER_STATES = {}


def get_invite_link(bot_username, user_id):
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


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


def generate_content_ideas(topic: str) -> str:
    return (
        f"🧠 5 أفكار محتوى عن: {topic}\n\n"
        f"1) 3 أخطاء شائعة في {topic}\n"
        f"   البداية: لا ترتكب هذا الخطأ إذا كنت مهتمًا بـ {topic}\n"
        f"   CTA: اكتب رأيك في التعليقات\n\n"
        f"2) أفضل نصيحة للمبتدئين في {topic}\n"
        f"   البداية: لو كنت تبدأ اليوم في {topic} فاسمع هذه النصيحة\n"
        f"   CTA: احفظ الفيديو\n\n"
        f"3) يوم في حياة شخص يعمل في {topic}\n"
        f"   البداية: هل تريد أن تعرف كيف يبدو يومي في {topic}؟\n"
        f"   CTA: تابع للمزيد\n\n"
        f"4) مقارنة قبل/بعد في {topic}\n"
        f"   البداية: الفرق بين قبل وبعد في {topic} صادم\n"
        f"   CTA: شارك الفيديو\n\n"
        f"5) أسرار النجاح في {topic}\n"
        f"   البداية: هذه أسرار لا يخبرك بها أحد في {topic}\n"
        f"   CTA: هل تريد جزءًا ثانيًا؟"
    )


def generate_caption(topic: str) -> str:
    return (
        f"✍️ 3 كابشنات عن: {topic}\n\n"
        f"1) إذا كنت تحب {topic} فهذا المحتوى لك 🔥\n\n"
        f"2) أسرار {topic} التي لا يخبرك بها أحد 👀\n\n"
        f"3) كل شيء يبدأ بخطوة... واليوم نتكلم عن {topic} 🚀"
    )


def generate_hashtags(topic: str) -> str:
    clean = topic.replace(" ", "_")
    return (
        f"#️⃣ هاشتاغات مناسبة لـ {topic}\n\n"
        f"#{clean} #{topic} #viral #fyp #reels #content #trend #tiktok #explore #video"
    )


def generate_script(topic: str) -> str:
    return (
        f"🎬 سكربت فيديو عن: {topic}\n\n"
        f"المشهد 1: بداية قوية\n"
        f"\"إذا كنت مهتمًا بـ {topic} فانتبه لهذا!\"\n\n"
        f"المشهد 2: شرح مختصر\n"
        f"قدّم أهم نقطة بشكل سريع وواضح.\n\n"
        f"المشهد 3: مثال\n"
        f"اعرض مثالًا أو تجربة أو نتيجة.\n\n"
        f"المشهد 4: النهاية\n"
        f"\"إذا أعجبك الفيديو تابعني للمزيد عن {topic}\""
    )


def generate_image_prompt(topic: str) -> str:
    return (
        f"🖼️ طلب صورة جاهز عن: {topic}\n\n"
        f"Prompt:\n"
        f"Ultra realistic {topic}, cinematic lighting, high detail, sharp focus, dramatic composition, 4k, realistic textures, professional photography style.\n\n"
        f"Negative Prompt:\n"
        f"low quality, blurry, distorted, extra limbs, bad anatomy, watermark, text.\n\n"
        f"Suggested Ratio: 1:1 أو 9:16"
    )


def generate_video_prompt(topic: str) -> str:
    return (
        f"🎥 طلب فيديو جاهز عن: {topic}\n\n"
        f"Video Prompt:\n"
        f"Create a short cinematic video about {topic}. "
        f"Make it realistic, smooth camera movement, dramatic lighting, high detail, "
        f"emotional atmosphere, social-media friendly, vertical 9:16.\n\n"
        f"اقتراح المشاهد:\n"
        f"1) لقطة افتتاحية قوية\n"
        f"2) حركة كاميرا بطيئة على العنصر الرئيسي\n"
        f"3) لقطة وسطية فيها تفاصيل واضحة\n"
        f"4) نهاية جذابة مناسبة لريلز أو تيك توك"
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
        await update.message.reply_text(
            TEXTS[LANG]["invite_text"].format(link=invite_link)
        )
        return

    if msg == TEXTS[LANG]["my_ref"]:
        count = get_referrals(user.id)
        await update.message.reply_text(
            TEXTS[LANG]["ref_count"].format(count=count)
        )
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
        await update.message.reply_text(generate_content_ideas(msg))
        USER_STATES.pop(user.id, None)
        return

    if state == "captions":
        await update.message.reply_text(generate_caption(msg))
        USER_STATES.pop(user.id, None)
        return

    if state == "hashtags":
        await update.message.reply_text(generate_hashtags(msg))
        USER_STATES.pop(user.id, None)
        return

    if state == "video_script":
        await update.message.reply_text(generate_script(msg))
        USER_STATES.pop(user.id, None)
        return

    if state == "image_ai":
        await update.message.reply_text(generate_image_prompt(msg))
        USER_STATES.pop(user.id, None)
        return

    if state == "video_ai":
        await update.message.reply_text(generate_video_prompt(msg))
        USER_STATES.pop(user.id, None)
        return


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