# handlers/main.py
from telegram import Update
from telegram.ext import CallbackContext
from config import REPLY_MARKUP, INFO_TEXT, MAIN_MENU
from utils.user_progress import UserProgress

# Создаем экземпляр UserProgress здесь
user_progress = UserProgress()

async def start(update: Update, context: CallbackContext) -> int:
    """Команда /start"""
    user_id = update.effective_user.id
    progress = user_progress.get_user_progress(user_id)
    
    welcome_text = f"""👋 Привет, {update.effective_user.first_name}!
    
🎮 Добро пожаловать в квест '4 уровня загадок'!
    
📊 Твой текущий прогресс:
Уровень 1 (Азия): {'✅ Пройден' if progress['level1_completed'] else '❌ Не пройден'}
Уровень 2 (Ассоциации): {'✅ Пройден' if progress['level2_completed'] else '❌ Не пройден'}
Уровень 3 (Шифр): {'✅ Пройден' if progress['level3_completed'] else '❌ Не пройден'}
Уровень 4 (Животные): {'✅ Пройден' if progress['level4_completed'] else '❌ Не пройден'}
    
Подсказок собрано: {progress['hints_collected']}/4
    
Используй кнопки ниже, чтобы продолжить!"""
    
    await update.message.reply_text(welcome_text, reply_markup=REPLY_MARKUP)
    return MAIN_MENU

async def get_info(update: Update, context: CallbackContext) -> int:
    """Показать информацию о боте"""
    await update.message.reply_text(INFO_TEXT, reply_markup=REPLY_MARKUP)
    return MAIN_MENU

async def handle_main_menu(update: Update, context: CallbackContext) -> int:
    """Обработка главного меню"""
    text = update.message.text
    
    if text == "🚀 Начать квест":
        from handlers.progress_handler import start_quest
        return await start_quest(update, context)
    elif text == "ℹ️ Информация":
        return await get_info(update, context)
    elif text == "📊 Мой прогресс":
        from handlers.progress_handler import show_progress
        return await show_progress(update, context)
    elif text == "🔄 Сбросить прогресс":
        from handlers.progress_handler import reset_progress
        return await reset_progress(update, context)
    else:
        await update.message.reply_text(
            "Используйте кнопки ниже для навигации:",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU