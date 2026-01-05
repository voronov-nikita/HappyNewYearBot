# handlers/level2_handler.py
from telegram import Update
from telegram.ext import CallbackContext
from config import MAIN_MENU, LEVEL_2_ASSOCIATION, REPLY_MARKUP
from utils.user_progress import UserProgress
from utils.file_loader import get_random_association
from utils.image_sender import send_image

user_progress = UserProgress()

async def start_level2(update: Update, context: CallbackContext) -> int:
    """Запуск уровня 2"""
    image_name, correct_answer = get_random_association()
    context.user_data["level2_answer"] = correct_answer
    context.user_data["level2_image"] = image_name
    
    # Отправляем изображение
    await send_image(update, context, image_name)
    
    await update.message.reply_text(
        "🧠 Уровень 2: Ассоциации по картинке\n\n"
        "Посмотрите на изображение и напишите слово или фразу, которая у вас ассоциируется.\n"
        "Введите ваш ответ:"
    )
    return LEVEL_2_ASSOCIATION

async def check_level2_answer(update: Update, context: CallbackContext) -> int:
    """Проверка ответа на уровень 2"""
    user_id = update.effective_user.id
    user_answer = update.message.text.strip().lower()
    correct_answer = context.user_data.get("level2_answer", "").lower()
    
    if user_answer == correct_answer:
        user_progress.update_level_completion(user_id, 2)
        
        await update.message.reply_text(
            f"✅ Верно! Картинка ассоциируется с '{correct_answer}'.\n\n"
            f"Вы прошли Уровень 2!\n"
            f"Получена подсказка к паролю: **0**\n\n"
            f"Нажмите 'Начать квест' для продолжения.",
            parse_mode="Markdown",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU
    else:
        await update.message.reply_text(
            f"❌ Неправильно!\n"
            f"Попробуйте снова, нажав 'Начать квест'.",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU