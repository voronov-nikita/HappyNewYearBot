# handlers/level3_handler.py
import re
from telegram import Update
from telegram.ext import CallbackContext
from config import MAIN_MENU, LEVEL_3_CAESAR_CIPHER, REPLY_MARKUP
from utils.user_progress import UserProgress
from utils.file_loader import load_caesar_data

user_progress = UserProgress()

async def start_level3(update: Update, context: CallbackContext) -> int:
    """Запуск уровня 3"""
    encrypted_text, decrypted_text, correct_answer = load_caesar_data()
    
    # Сохраняем правильный ответ
    context.user_data["level3_answer"] = correct_answer
    
    await update.message.reply_text(
        f"🔐 Уровень 3: Шифр Цезаря\n\n"
        f"Перед вами зашифрованный текст. Расшифруйте его и впишите пропущенное слово.\n\n"
        f"Зашифрованный текст:\n{encrypted_text}\n\n"
        f"Введите пропущенное слово:"
    )
    return LEVEL_3_CAESAR_CIPHER

async def check_level3_answer(update: Update, context: CallbackContext) -> int:
    """Проверка ответа на уровень 3"""
    user_id = update.effective_user.id
    user_answer = update.message.text.strip().lower()
    correct_answer = context.user_data.get("level3_answer", "").lower()
    
    if user_answer == correct_answer:
        user_progress.update_level_completion(user_id, 3)
        
        await update.message.reply_text(
            f"✅ Верно! Пропущенное слово: '{correct_answer}'.\n\n"
            f"Вы прошли Уровень 3!\n"
            f"Получена подсказка к паролю: **2**\n\n"
            f"Нажмите 'Начать квест' для продолжения.",
            parse_mode="Markdown",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU
    else:
        await update.message.reply_text(
            f"❌ Неправильно!\n"
            f"Правильный ответ: {correct_answer}\n"
            f"Попробуйте снова, нажав 'Начать квест'.",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU