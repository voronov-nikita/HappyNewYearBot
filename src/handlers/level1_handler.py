# handlers/level1_handler.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from config import MAIN_MENU, LEVEL_1_MULTIPLE_CHOICE
from utils.user_progress import UserProgress
from utils.file_loader import get_random_question

user_progress = UserProgress()

async def start_level1(update: Update, context: CallbackContext) -> int:
    """Запуск уровня 1"""
    question, q_index = get_random_question()
    context.user_data["current_question"] = question
    context.user_data["question_index"] = q_index
    context.user_data["current_level"] = 1
    
    keyboard = []
    for i, option in enumerate(question["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"level1_{i}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌏 Уровень 1: Вопрос про Азию\n\n"
        f"{question['question']}",
        reply_markup=reply_markup
    )
    return LEVEL_1_MULTIPLE_CHOICE

async def handle_level1_answer(update: Update, context: CallbackContext) -> int:
    """Обработка ответа на уровень 1"""
    from config import MAIN_MENU, REPLY_MARKUP
    
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    question = context.user_data.get("current_question", {})
    selected_answer = int(query.data.split("_")[1])
    
    if selected_answer == question.get("correct_answer", -1):
        user_progress.update_level_completion(user_id, 1)
        
        await query.edit_message_text(
            f"✅ Правильно! {question.get('explanation', '')}\n\n"
            f"Вы прошли Уровень 1!\n"
            f"Получена подсказка к паролю: **2**\n\n"
            f"Нажмите 'Начать квест' для продолжения.",
            parse_mode="Markdown"
        )
        return MAIN_MENU
    else:
        correct_idx = question.get("correct_answer", 0)
        correct_answer = question["options"][correct_idx] if correct_idx < len(question["options"]) else "Неизвестно"
        
        await query.edit_message_text(
            f"❌ Неправильно!\n"
            f"Правильный ответ: {correct_answer}\n"
            f"{question.get('explanation', '')}\n\n"
            f"Попробуйте снова, нажав 'Начать квест'.",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU