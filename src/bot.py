import os
import random
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# Уменьшаем логирование для скорости
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Изменено с INFO на WARNING для меньшего логгирования
)
logger = logging.getLogger(__name__)

# Также уменьшаем логирование сторонних библиотек
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

# Константы
CORRECT_PASSWORD = "ДЩМУ"

# Оптимизированные URL изображений (меньший размер для быстрой загрузки)
IMAGE_URLS = {
    2: "https://github.com/voronov-nikita/HappyNewYearBot/blob/main/src/img/elka.jpg?raw=true",
    4: "https://github.com/voronov-nikita/HappyNewYearBot/blob/main/src/img/god.jpeg?raw=true"
}

QUESTIONS = [
    {"type": "text", "question": "Загадка №1: Какой напиток приготовлен из побегов чайного куста 🫖, а не другого растения?", "answer": "пуэр"},
    {"type": "image", "question": "Загадка №2: Посмотри на изображение и угадай какую новогоднюю детскую песню 🎙️ зашифровали (здесь ответ состоит из нескольких слов, помни про букву `ё` 😉).",
        "answer": "в лесу родилась ёлочка", "image_url": IMAGE_URLS[2]},
    {"type": "text", 
    "question": 
        "Загадка №3: Это уже сложнее! Здесь нужно знать шифр Цезаря 🥬.\nНужно вставить пропущенное слово (важно соблюдать полную пунктуацию и значимость символов):\nХкцзбк лсфэубк юёцб хфезосочв з 1848 ифйщ з ифцфйрк Сёщю з Икцтёуоо. Оы чфнйёзёсо он ____ чшкрсё, хцфнцёэуфиф осо ьзкшуфиф.", 
        "answer": "тяжёлого"},
    {"type": "image", "question": "Загадка №4: Статуя какой богини 🙏, расположенная в Японии, изображена на этом фото?",
        "answer": "канон", "image_url": IMAGE_URLS[4]}
]

HINTS = {0: "Д", 1: "Щ", 2: "М", 3: "У"}

# Оптимизированное хранилище с тайм-аутом очистки
class FastUserData:
    def __init__(self):
        self.data = {}
        self.last_cleanup = asyncio.get_event_loop().time()
    
    def get_user(self, user_id):
        # Периодическая очистка устаревших данных (каждые 10 минут)
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_cleanup > 600:  # 10 минут
            self._cleanup()
            self.last_cleanup = current_time
        
        if user_id not in self.data:
            self.data[user_id] = {
                'answered_questions': [],
                'hints_collected': [],
                'awaiting_input': None,
                'last_active': current_time
            }
        else:
            self.data[user_id]['last_active'] = current_time
        return self.data[user_id]
    
    def _cleanup(self):
        """Очистка неактивных пользователей (больше 2 часов)"""
        current_time = asyncio.get_event_loop().time()
        inactive_users = []
        for user_id, data in self.data.items():
            if current_time - data.get('last_active', 0) > 7200:  # 2 часа
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            del self.data[user_id]

user_data = FastUserData()

welcome_text = '''🎅 Привет! Я бот, разработанный, чтобы ты могла получить свой подарок на Новый год. Тебе нужно пройти квест 🎄!\nВопросов будет 4, каждый из них не сложный, по тематике, которую ты точно должна знать или хотя бы слышала 😉.\nНомера вопросов пишутся и они же соответствуют букве или цифре пароля. \nВсего пароль состоит как раз из 4-х символов 🔒. Ответы на вопросы однозначные и односложные (в одно слово, но есть исключения). Возможно нужно будет поперебирать 😅.\n\nА теперь, выбери действие:'''

# Кэшированная клавиатура для скорости
_cached_keyboard = None

def get_main_keyboard():
    """Создает основную клавиатуру (кэшированную для скорости)"""
    global _cached_keyboard
    if _cached_keyboard is None:
        keyboard = [
            [InlineKeyboardButton("Инфо", callback_data='info')],
            [InlineKeyboardButton("Начать квест", callback_data='start_quest')],
            [InlineKeyboardButton("Ввести пароль", callback_data='enter_password')],
            [InlineKeyboardButton("Прогресс", callback_data='progress')]
        ]
        _cached_keyboard = InlineKeyboardMarkup(keyboard)
    return _cached_keyboard

async def send_image_fast(chat_id, image_url, caption, context):
    """Быстрая отправка изображения с таймаутом"""
    try:
        # Используем более короткий таймаут для скорости
        await asyncio.wait_for(
            context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=caption[:1024],  # Ограничиваем длину подписи для скорости
                read_timeout=15,
                write_timeout=15,
                connect_timeout=10
            ),
            timeout=20
        )
        return True
    except asyncio.TimeoutError:
        logger.warning(f"Таймаут при отправке изображения")
        return False
    except Exception as e:
        logger.warning(f"Ошибка отправки изображения: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый обработчик команды /start"""
    try:
        user_id = update.effective_user.id
        user_data.get_user(user_id)  # Инициализируем пользователя
        
        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())
        elif update.callback_query:
            await update.callback_query.message.reply_text(welcome_text, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оптимизированный обработчик кнопок"""
    query = update.callback_query
    await query.answer()  # Быстрый ответ на нажатие
    
    user_id = update.effective_user.id
    user = user_data.get_user(user_id)
    
    try:
        if query.data == 'info':
            await query.edit_message_text(welcome_text, reply_markup=get_main_keyboard())
        
        elif query.data == 'enter_password':
            user['awaiting_input'] = 'password'
            await query.edit_message_text("🔒 Введите пароль:", reply_markup=get_main_keyboard())
        
        elif query.data == 'start_quest':
            # Быстрый поиск доступных вопросов
            answered = set(user['answered_questions'])
            available_questions = [i for i in range(4) if i not in answered]
            
            if not available_questions:
                await query.edit_message_text(
                    "Вы уже ответили на все вопросы! 🥳🥳🥳.\nПереходите к вводу пароля.",
                    reply_markup=get_main_keyboard()
                )
                return
            
            question_num = random.choice(available_questions)
            question_data = QUESTIONS[question_num]
            user['awaiting_input'] = f'question_{question_num}'
            
            if question_data['type'] == 'text':
                await query.edit_message_text(
                    f"{question_data['question']}\n\nВведите ваш ответ:",
                    reply_markup=get_main_keyboard()
                )
            
            elif question_data['type'] == 'image':
                # Быстрый ответ перед загрузкой изображения
                await query.edit_message_text("Загружаю задание...", reply_markup=get_main_keyboard())
                
                # Отправляем изображение в фоне (не блокируем ответ)
                asyncio.create_task(send_quest_image_background(
                    chat_id=query.message.chat_id,
                    question_num=question_num,
                    question_data=question_data,
                    context=context
                ))
        
        elif query.data == 'progress':
            hints = user['hints_collected']
            hints_text = "🗝️ Вы собрали следующие буквы:\n" + " ".join(sorted(hints)) if hints else "Вы еще не собрали ни одной буквы."
            total_answered = len(user['answered_questions'])
            progress_text = f"Отвечено вопросов: {total_answered}/4\n\n{hints_text}"
            await query.edit_message_text(progress_text, reply_markup=get_main_keyboard())
    
    except Exception as e:
        logger.error(f"Ошибка в button_handler: {e}")
        try:
            await query.edit_message_text("Произошла ошибка 😢. Попробуйте еще раз.", reply_markup=get_main_keyboard())
        except:
            pass

async def send_quest_image_background(chat_id, question_num, question_data, context):
    """Асинхронная отправка изображения (не блокирует основной поток)"""
    try:
        image_url = question_data.get('image_url')
        if image_url:
            sent = await send_image_fast(
                chat_id=chat_id,
                image_url=image_url,
                caption=f"{question_data['question']}\n\nВведите ваш ответ:",
                context=context
            )
            if not sent:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{question_data['question']}\n\nВведите ваш ответ:",
                    reply_markup=get_main_keyboard()
                )
    except Exception as e:
        logger.error(f"Ошибка отправки изображения в фоне: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый обработчик текстовых сообщений"""
    try:
        user_id = update.effective_user.id
        user = user_data.get_user(user_id)
        user_input = update.message.text.strip().lower()
        
        # Быстрая проверка состояния
        if user['awaiting_input'] == 'password':
            if user_input == CORRECT_PASSWORD.lower():
                response = '''✅ Пароль верный! 🥳🎉🥳.
                \nПоздравляю, ты заслужила свой подарок 😉.
                \nНапиши мне лично, чтобы я мы могли договориться о месте и времени передачи 🎅.
                \nМой ТГ: @not_data_user
                '''
            else:
                response = "❌ Неверный пароль. Попробуй еще раз."
            
            user['awaiting_input'] = None
            await update.message.reply_text(response, reply_markup=get_main_keyboard())
        
        elif user['awaiting_input'] and user['awaiting_input'].startswith('question_'):
            question_num = int(user['awaiting_input'].split('_')[1])
            question_data = QUESTIONS[question_num]
            
            if user_input == question_data['answer'].lower():
                user['answered_questions'].append(question_num)
                
                if question_num in HINTS:
                    hint = HINTS[question_num]
                    user['hints_collected'].append(hint)
                    response = f"✅ Правильно! Вы получаете букву: {hint}"
                else:
                    response = "✅ Правильно!"
            else:
                response = "❌ Неправильно. Попробуйте еще раз."
            
            user['awaiting_input'] = None
            await update.message.reply_text(response, reply_markup=get_main_keyboard())
        
        else:
            await update.message.reply_text(
                "Я не знаю такой команды. Пожалуйста, используй только кнопки ниже:",
                reply_markup=get_main_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок для стабильности"""
    logger.error(f"Exception: {context.error}")
    if update and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Произошла ошибка 😢. Попробуйте еще раз.",
                reply_markup=get_main_keyboard()
            )
        except:
            pass

def main():
    """Основная функция с оптимизированными настройками"""
    TOKEN = ""
    
    # Оптимизированные настройки для скорости
    application = Application.builder()\
        .token(TOKEN)\
        .read_timeout(15)\
        .write_timeout(15)\
        .connect_timeout(10)\
        .pool_timeout(10)\
        .get_updates_read_timeout(15)\
        .build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Оптимизированный polling
    logger.info("Бот запущен с оптимизациями...")
    
    # Важно: используем эти настройки для скорости
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        poll_interval=0.1,  # Уменьшен интервал опроса
        timeout=15,
        close_loop=False
    )

if __name__ == "__main__":
    # Устанавливаем переменные окружения для производительности
    os.environ['PYTHONASYNCIODEBUG'] = '0'
    
    # Запускаем с оптимизациями
    try:
        main()
    except KeyboardInterrupt:
        print("\nБот остановлен.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")