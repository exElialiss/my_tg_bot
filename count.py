import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

BOT_TOKEN = '7482589176:AAGiC_49FdRxKvw7zWXFB1fQdEEFfKYavVw'

# Переменная для хранения даты встречи
meeting_date = None

# Планировщик для отправки сообщений
scheduler = BackgroundScheduler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Введите дату встречи командой /setdate YYYY-MM-DD.")

async def setdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global meeting_date

    try:
        # Парсим дату встречи
        date_str = context.args[0]
        meeting_date = datetime.strptime(date_str, '%Y-%m-%d')

        # Отправляем первое сообщение сразу
        await send_days_left_message(update.message.chat_id)

        # Запускаем ежедневные уведомления
        chat_id = update.message.chat_id
        scheduler.add_job(send_daily_message, 'interval', days=1, args=[chat_id], next_run_time=datetime.now() + timedelta(days=1))
        scheduler.start()

    except (IndexError, ValueError):
        await update.message.reply_text("Неправильный формат даты. Введите команду так: /setdate YYYY-MM-DD.")

async def send_days_left_message(chat_id):
    global meeting_date

    if meeting_date:
        today = datetime.now()
        days_left = (meeting_date - today).days

        if days_left > 0:
            message = f"До встречи осталось {days_left} дней!"
        elif days_left == 0:
            message = "Сегодня встреча!"
        else:
            message = "Дата встречи уже прошла."

        # Отправляем сообщение сразу
        await application.bot.send_message(chat_id=chat_id, text=message)

async def send_daily_message(chat_id):
    # Эта функция вызывается каждый день планировщиком
    await send_days_left_message(chat_id)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понимаю эту команду.")

if __name__ == '__main__':
    # Создаем приложение Telegram
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setdate", setdate))

    # Регистрируем обработчик для неизвестных команд
    application.add_handler(CommandHandler("unknown", unknown))

    print("Бот запущен...")

    # Запускаем бота
    application.run_polling()
