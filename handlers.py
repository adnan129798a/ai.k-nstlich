from telegram import Update
from telegram.ext import ContextTypes

from database import add_user, set_referral, get_referrals
from texts import TEXTS
from keyboards import menu, unlock_keyboard
from config import REQUIRED_CHANNEL_URL


LANG = "ar"


def get_invite_link(bot_username, user_id):
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member("@ai_creator_hub2025", user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)

    if context.args:
        ref = context.args[0]
        if ref.startswith("ref_"):
            referrer = int(ref.replace("ref_", ""))
            if referrer != user.id:
                set_referral(user.id, referrer)

    await update.message.reply_text(
        TEXTS[LANG]["welcome"],
        reply_markup=menu(LANG)
    )


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message.text
    invite_link = get_invite_link(context.bot.username, user.id)

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
            await update.message.reply_text(TEXTS[LANG]["image_ok"])
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
            await update.message.reply_text(TEXTS[LANG]["video_ok"])
        return


async def check_unlock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user

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