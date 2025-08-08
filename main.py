from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random
import sqlite3

TOKEN = "8091412559:AAHgqI_YrIiVrgIQ5jWhmMvtaV_2aSglNrg"  # <-- Замени на свой токен

conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, attempts INTEGER, bonus_used INTEGER)''')
conn.commit()

SECRET_NUMBER = 7

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id, attempts, bonus_used) VALUES (?, 0, 0)", (user_id,))
    conn.commit()
    await update.message.reply_text("Угадай число от 1 до 10. У тебя 3 попытки!")

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT attempts, bonus_used FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if not result:
        await update.message.reply_text("Сначала напиши /start")
        return

    attempts, bonus_used = result
    if bonus_used:
        await update.message.reply_text("Ты уже использовал бонус.")
        return

    if attempts >= 3:
        await update.message.reply_text("Попытки закончились.")
        return

    try:
        guess = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введи число.")
        return

    cursor.execute("UPDATE users SET attempts = attempts + 1 WHERE user_id=?", (user_id,))
    conn.commit()

    if guess == SECRET_NUMBER:
        cursor.execute("UPDATE users SET bonus_used = 1 WHERE user_id=?", (user_id,))
        conn.commit()
        await update.message.reply_text("Поздравляю! Ты выиграл 5% скидку. Закажи рекламу по ссылке: https://vk.me/public")
    else:
        await update.message.reply_text("Не угадал. Попробуй снова.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_guess))
    app.run_polling()
