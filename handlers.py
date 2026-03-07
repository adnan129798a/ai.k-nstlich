if msg == TEXTS[LANG]["video_ai"]:
    refs = get_referrals(user.id)
    subscribed = await is_subscribed(user.id, context)
    if refs < 1 or not subscribed:
        await update.message.reply_text(
            TEXTS[LANG]["locked"],
            reply_markup=unlock_keyboard(LANG, REQUIRED_CHANNEL_URL, invite_link)
        )
    else:
        _video_defaults(user.id)
        await update.message.reply_text(
            TEXTS[LANG]["video_menu_intro"],
            reply_markup=video_menu_keyboard(LANG)
        )
    return