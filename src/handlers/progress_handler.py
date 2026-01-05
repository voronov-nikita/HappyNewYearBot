# handlers/progress.py
from telegram import Update
from telegram.ext import CallbackContext
from config import REPLY_MARKUP, ENTER_FINAL_PASSWORD, MAIN_MENU
from handlers.main import UserProgress
from handlers import level1_handler, level2_handler, level3_handler, level4_handler

user_progress = UserProgress()

def start_quest(update: Update, context: CallbackContext) -> int:
    """Начало квеста или продолжение с текущего уровня"""
    user_id = update.effective_user.id
    progress = user_progress.get_user_progress(user_id)
    
    current_level = progress["current_level"]
    
    if current_level == 1:
        update.message.reply_text("🌏 Начинаем Уровень 1: Вопрос про Азию!")
        return level1_handler.start_level1(update, context)
    elif current_level == 2 and progress["level1_completed"]:
        update.message.reply_text("🧠 Переходим к Уровню 2: Ассоциации по картинке!")
        return level2_handler.start_level2(update, context)
    elif current_level == 3 and progress["level2_completed"]:
        update.message.reply_text("🔐 Добро пожаловать на Уровень 3: Шифр Цезаря!")
        return level3_handler.start_level3(update, context)
    elif current_level == 4 and progress["level3_completed"]:
        update.message.reply_text("🐾 Начинаем Уровень 4: Найди животное на фото!")
        return level4_handler.start_level4(update, context)
    elif progress["level4_completed"]:
        update.message.reply_text(
            "🎊 Поздравляем! Вы прошли все уровни!\n"
            "Теперь введите финальный пароль из 4 символов:"
        )
        return ENTER_FINAL_PASSWORD
    else:
        update.message.reply_text(
            "⚠️ Сначала нужно пройти предыдущий уровень!\n"
            "Используйте кнопку 'Мой прогресс' для проверки.",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU

def show_progress(update: Update, context: CallbackContext) -> int:
    """Показать прогресс пользователя"""
    user_id = update.effective_user.id
    progress = user_progress.get_user_progress(user_id)
    
    progress_text = f"""📊 Ваш прогресс:

Уровень 1 (Азия): {'✅ Пройден' if progress['level1_completed'] else '❌ Не пройден'}
Уровень 2 (Ассоциации): {'✅ Пройден' if progress['level2_completed'] else '❌ Не пройден'}
Уровень 3 (Шифр Цезаря): {'✅ Пройден' if progress['level3_completed'] else '❌ Не пройден'}
Уровень 4 (Найди животное): {'✅ Пройден' if progress['level4_completed'] else '❌ Не пройден'}

Текущий уровень: {progress['current_level']}
Подсказок собрано: {progress['hints_collected']}/4

"""
    
    if progress['level4_completed']:
        progress_text += "🎉 Вы прошли все уровни! Введите финальный пароль.\n"
        progress_text += "Подсказка: 2024"
    else:
        progress_text += "Продолжайте квест, нажав 'Начать квест'!"
    
    update.message.reply_text(progress_text, reply_markup=REPLY_MARKUP)
    return MAIN_MENU

def reset_progress(update: Update, context: CallbackContext) -> int:
    """Сбросить прогресс пользователя"""
    user_id = update.effective_user.id
    user_progress.reset_progress(user_id)
    
    update.message.reply_text(
        "🔄 Ваш прогресс сброшен!\n"
        "Начните квест заново, нажав 'Начать квест'.",
        reply_markup=REPLY_MARKUP
    )
    return MAIN_MENU

def check_final_password(update: Update, context: CallbackContext) -> int:
    """Проверка финального пароля"""
    from config import FINAL_PASSWORD, REPLY_MARKUP, MAIN_MENU
    
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    
    if user_input == FINAL_PASSWORD:
        congrats_text = """🎊🎊🎊 ПОЗДРАВЛЯЕМ! 🎊🎊🎊

Вы успешно прошли все 4 уровня и разгадали финальный пароль!

🏆 Ваши достижения:
• Ответили на вопрос про Азию
• Разгадали ассоциации по картинке
• Расшифровали шифр Цезаря
• Нашли всех животных

🎁 Вы заслужили это поздравление!
Желаем вам новых побед и интересных квестов!

Спасибо за игру! 🚀"""
        
        update.message.reply_text(congrats_text, reply_markup=REPLY_MARKUP)
        return MAIN_MENU
    else:
        update.message.reply_text(
            "❌ Неверный пароль! Попробуйте еще раз.\n"
            "Вспомните подсказки с каждого уровня.",
            reply_markup=REPLY_MARKUP
        )
        return ENTER_FINAL_PASSWORD