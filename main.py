from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from handlers import (
    start,
    text,
    check_unlock_callback,
    image_style_callback,
    photo_handler,
    photo_edit_callback,
    video_callback,
)
from database import init_db
from config import BOT_TOKEN

init_db()

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_unlock_callback, pattern="^check_unlock$"))
app.add_handler(CallbackQueryHandler(image_style_callback, pattern="^img_"))
app.add_handler(CallbackQueryHandler(photo_edit_callback, pattern="^edit_"))
app.add_handler(CallbackQueryHandler(video_callback, pattern="^(video_|vm_|vl_|vr_)"))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))

app.run_polling()