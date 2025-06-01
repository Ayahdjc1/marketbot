# bot.py

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from admin_utils import admin_help, generate_admin_report, generate_range_report
from database import create_engagement_table
from config import API_TOKEN  # Импорт конфигурации
import requests 
# === Логирование ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Команда /start ===
def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    update.message.reply_text(
        "👋 Привет! Я бот для аналитики Telegram-канала.\n\n"
        "📊 Основные команды:\n"
        "/report <период> — отчёт по стандартному периоду\n"
        "Например: /report daily | week | month | year\n\n"
        "/report_range <дата_от> <дата_до> — отчёт за диапазон дат\n"
        "Формат: /report_range 2025-05-01 2025-05-10\n\n"
        "📅 Все даты указываются в формате YYYY-MM-DD"
    )
from database import execute_query

def debug_show_data(update: Update, context: CallbackContext):
    rows = execute_query("SELECT post_id, date, likes, comments, shares FROM engagement_data ORDER BY date DESC LIMIT 10")
    if not rows:
        update.message.reply_text("База пуста.")
    else:
        text = "\n".join([f"{r[1]} — 👍{r[2]} 💬{r[3]} 🔁{r[4]}" for r in rows])
        update.message.reply_text("📊 Последние записи:\n" + text[:4000])

# === Обработка ошибок ===
def error_handler(update, context):
    """Логирование ошибок"""
    logger.warning(f'⚠️ Ошибка: {context.error}')

# === Главная функция ===
def main():
    # Инициализация базы данных
    create_engagement_table()

    # Инициализация бота
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрация обработчиков команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_help))
    dp.add_handler(CommandHandler("report", generate_admin_report, pass_args=True))
    dp.add_handler(CommandHandler("report_range", generate_range_report, pass_args=True))
    dp.add_handler(CommandHandler("debug", debug_show_data))

    # Обработчик ошибок
    dp.add_error_handler(error_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
