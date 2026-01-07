import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
CORRECT_PASSWORD = "секрет123"

# Только текстовые задания (без изображений)
QUESTIONS = [
    {"type": "text", "question": "Загадка №1: Что можно сломать, даже если никогда не касаешься этого?", "answer": "обещание"},
    {"type": "text", "question": "Загадка №2: Что имеет ключ, но не открывает замки?", "answer": "пианино"},
    {"type": "text", "question": "Загадка №3: Я легок, как перо, но самый сильный человек не может удержать меня долго. Что я?", "answer": "дыхание"},
    {"type": "text", "question": "Загадка №4: Чем больше берешь, тем больше оставляешь. Что это?", "answer": "шаги"}
]

HINTS = {0: "П", 1: "А", 2: "Р", 3: "О"}

# Простое хранилище в памяти
user_states = {}

def get_user_state(user_id):
    """Получает состояние пользователя"""
    if user_id not in user_states:
        user_states[user_id] = {
            'answered': [],
            'hints': [],
            'awaiting': None
        }
    return user_states[user_id]

def get_main_keyboard():
    """Создает клавиатуру"""
    keyboard = [
        [InlineKeyboardButton("Инфо", callback_data='info')],
        [InlineKeyboardButton("Начать квест", callback_data='start_quest')],
        [InlineKeyboardButton("Ввести пароль", callback_data='enter_password')],
        [InlineKeyboardButton("Прогресс", callback_data='progress')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Асинхронные функции (как требует библиотека)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Создаем состояние пользователя если нужно
    get_user_state(user_id)
    
    # Отправляем приветствие
    await update.message.reply_text(
        "Привет! Я бот для квеста. Выберите действие:",
        reply_markup=get_main_keyboard()
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия кнопок"""
    query = update.callback_query
    await query.answer()  # Убираем "часики" у кнопки
    
    user_id = update.effective_user.id
    user_state = get_user_state(user_id)
    
    if query.data == 'info':
        await query.edit_message_text(
            "Привет! Я бот для квеста. Выберите действие:",
            reply_markup=get_main_keyboard()
        )
    
    elif query.data == 'enter_password':
        user_state['awaiting'] = 'password'
        await query.edit_message_text(
            "Введите пароль:",
            reply_markup=get_main_keyboard()
        )
    
    elif query.data == 'start_quest':
        # Находим доступные вопросы
        available = [i for i in range(len(QUESTIONS)) if i not in user_state['answered']]
        
        if not available:
            await query.edit_message_text(
                "Вы уже ответили на все вопросы!",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Выбираем случайный вопрос
        question_num = random.choice(available)
        question_data = QUESTIONS[question_num]
        
        # Запоминаем, что ждем ответ на этот вопрос
        user_state['awaiting'] = f'question_{question_num}'
        
        await query.edit_message_text(
            f"{question_data['question']}\n\nВведите ваш ответ:",
            reply_markup=get_main_keyboard()
        )
    
    elif query.data == 'progress':
        hints = user_state['hints']
        if hints:
            hints_text = "Вы собрали следующие буквы:\n" + " ".join(sorted(hints))
        else:
            hints_text = "Вы еще не собрали ни одной буквы."
        
        total = len(user_state['answered'])
        progress_text = f"Отвечено вопросов: {total}/4\n\n{hints_text}"
        
        await query.edit_message_text(
            progress_text,
            reply_markup=get_main_keyboard()
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_state = get_user_state(user_id)
    user_input = update.message.text.strip().lower()
    
    # Если бот ожидает ввод пароля
    if user_state['awaiting'] == 'password':
        if user_input == CORRECT_PASSWORD.lower():
            response = "✅ Пароль верный! Вы получили доступ к секретному материалу."
        else:
            response = "❌ Неверный пароль. Попробуйте еще раз."
        
        user_state['awaiting'] = None
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # Если бот ожидает ответ на вопрос
    elif user_state['awaiting'] and user_state['awaiting'].startswith('question_'):
        question_num = int(user_state['awaiting'].split('_')[1])
        question_data = QUESTIONS[question_num]
        
        if user_input == question_data['answer'].lower():
            # Правильный ответ
            user_state['answered'].append(question_num)
            
            # Даем подсказку
            if question_num in HINTS:
                hint = HINTS[question_num]
                user_state['hints'].append(hint)
                response = f"✅ Правильно! Вы получаете букву: {hint}"
            else:
                response = "✅ Правильно!"
        else:
            # Неправильный ответ
            response = "❌ Неправильно. Попробуйте еще раз."
        
        user_state['awaiting'] = None
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    else:
        # Пользователь отправил что-то неожиданное
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для взаимодействия:",
            reply_markup=get_main_keyboard()
        )

def main():
    """Главная функция"""
    # Ваш токен от BotFather
    TOKEN = "8061720392:AAE-ELJI9P3Do3EAyGloHErdmAWXF088LU0"
    
    try:
        # Создаем приложение с минимальными настройками
        app = Application.builder().token(TOKEN).build()
        
        # Регистрируем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_click))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Запускаем бота
        logger.info("Бот запущен...")
        app.run_polling(
            drop_pending_updates=True,
            timeout=30,
            poll_interval=0.5
        )
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        print(f"Критическая ошибка: {e}")

# Альтернативный запуск без polling (если polling не работает)
def main_simple():
    """Упрощенный запуск"""
    TOKEN = "8061720392:AAE-ELJI9P3Do3EAyGloHErdmAWXF088LU0"
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()