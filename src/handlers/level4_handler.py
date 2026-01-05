# handlers/level4_handler.py
from telegram import Update
from telegram.ext import CallbackContext
from config import MAIN_MENU, LEVEL_4_FIND_ANIMAL, REPLY_MARKUP, ENTER_FINAL_PASSWORD
from utils.user_progress import UserProgress
from utils.file_loader import get_random_animal
from utils.image_sender import send_image

user_progress = UserProgress()

async def start_level4(update: Update, context: CallbackContext) -> int:
    """Запуск уровня 4"""
    image_name, correct_answer = get_random_animal()
    context.user_data["level4_answer"] = correct_answer
    context.user_data["level4_image"] = image_name
    
    # Отправляем изображение
    await send_image(update, context, image_name)
    
    await update.message.reply_text(
        "🐾 Уровень 4: Найди животное на фото\n\n"
        "Посмотрите на изображение и напишите название животного.\n"
        "Введите ваш ответ:"
    )
    return LEVEL_4_FIND_ANIMAL

async def check_level4_answer(update: Update, context: CallbackContext) -> int:
    """Проверка ответа на уровень 4"""
    user_id = update.effective_user.id
    user_answer = update.message.text.strip().lower()
    correct_answer = context.user_data.get("level4_answer", "").lower()
    
    if user_answer == correct_answer:
        user_progress.update_level_completion(user_id, 4)
        
        await update.message.reply_text(
            f"✅ Правильно! Это действительно {correct_answer}.\n\n"
            f"🎉 БРАВО! Вы прошли все 4 уровня! 🎉\n\n"
            f"✅ Уровень 4 пройден!\n"
            f"Получена финальная подсказка к паролю: **4**\n\n"
            f"Теперь соберите все подсказки:\n"
            f"Уровень 1: 2\n"
            f"Уровень 2: 0\n"
            f"Уровень 3: 2\n"
            f"Уровень 4: 4\n\n"
            f"Получился пароль: **2024**\n\n"
            f"Введите финальный пароль, чтобы получить поздравление:",
            parse_mode="Markdown"
        )
        return ENTER_FINAL_PASSWORD
    else:
        await update.message.reply_text(
            f"❌ Неправильно!\n"
            f"Попробуйте снова, нажав 'Начать квест'.",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU