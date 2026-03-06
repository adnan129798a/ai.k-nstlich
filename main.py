from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from handlers import start, text, check_unlock_callback
from database import init_db
from config import BOT_TOKEN

init_db()

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_unlock_callback, pattern="^check_unlock$"))
app.add_handler(MessageHandler(filters.TEXT, text))

app.run_polling()