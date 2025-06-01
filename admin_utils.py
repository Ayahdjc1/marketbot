# admin_utils.py

from telegram import Update
from telegram.ext import CallbackContext
from report_generator import ReportGenerator
from config import ADMIN_IDS
import logging

# Инициализация генератора отчетов
report_generator = ReportGenerator()
logger = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return user_id in ADMIN_IDS

def admin_help(update: Update, context: CallbackContext):
    """Показать админ-команды"""
    if not is_admin(update.effective_user.id):
        update.message.reply_text("⛔ Доступ запрещён.")
        return

    update.message.reply_text(
        "🔐 Админ-команды:\n"
        "/report <период> — отчёт (daily/week/month/year)\n"
        "/report_range <начало> <конец> — отчёт за диапазон дат\n"
        "/admin — список команд"
    )

def _check_admin_access(func):
    """Декоратор для проверки прав администратора"""
    def wrapper(update: Update, context: CallbackContext):
        if not is_admin(update.effective_user.id):
            update.message.reply_text("⛔ У вас нет прав.")
            return
        return func(update, context)
    return wrapper

@_check_admin_access
def generate_admin_report(update: Update, context: CallbackContext):
    """Генерация периодического отчета"""
    if not context.args:
        update.message.reply_text("⚠️ Укажите период: /report daily/week/month/year")
        return

    period = context.args[0].lower()
    try:
        # Используем метод класса ReportGenerator
        path = report_generator.generate_report(period)
        with open(path, "rb") as doc:
            update.message.reply_document(document=doc)
    except ValueError as ve:
        update.message.reply_text(f"⚠️ Ошибка входных данных: {ve}")
        logger.error(f"Validation error: {ve}")
    except Exception as e:
        update.message.reply_text("❌ Ошибка генерации отчета")
        logger.critical(f"Report generation failed: {e}", exc_info=True)

@_check_admin_access
def generate_range_report(update: Update, context: CallbackContext):
    """Генерация отчета за диапазон дат"""
    if len(context.args) != 2:
        update.message.reply_text("⚠️ Использование: /report_range <начало> <конец>\nФормат: YYYY-MM-DD")
        return

    start_date, end_date = context.args
    try:
        # Используем метод класса ReportGenerator
        path = report_generator.generate_report_by_date_range(start_date, end_date)
        with open(path, "rb") as doc:
            update.message.reply_document(document=doc)
    except ValueError as ve:
        update.message.reply_text(f"⚠️ Некорректные даты: {ve}")
        logger.warning(f"Date validation failed: {ve}")
    except Exception as e:
        update.message.reply_text("❌ Ошибка генерации отчета")
        logger.critical(f"Range report failed: {e}", exc_info=True)
