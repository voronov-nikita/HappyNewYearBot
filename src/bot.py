import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
CORRECT_PASSWORD = "ДЩМУ"

# Используем прямые ссылки на изображения
IMAGE_URLS = {
    2: "https://github.com/voronov-nikita/HappyNewYearBot/blob/main/src/img/elka.jpg?raw=true",
    # Замените на реальные ссылки
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
user_data = {}

welcome_text = '''
    🎅 Привет! Я бот, разработанный, чтобы ты могла получить свой подарок на Новый год. Тебе нужно пройти квест 🎄!\nВопросов будет 4, каждый из них не сложный, по тематике, которую ты точно должна знать или хотя бы слышала 😉.\nНомера вопросов пишутся и они же соответствуют букве или цифре пароля. \nВсего пароль состоит как раз из 4-х символов 🔒. Ответы на вопросы однозначные и односложные (в одно слово, но есть исключения). Возможно нужно будет поперебирать 😅.\n\n😔 По правде сказать, бот работает так себе и иногда нужно долго подождать ответа или вообще тыкать много-много раз на кнопку, чтобы получить от нее результат... 🤖 Прости, бот делался быстро... даже слишком.\n\nА теперь, выбери действие:'''


async def send_image_from_url(chat_id, image_url, caption, context):
    """Отправляет изображение по URL"""
    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=caption,
            parse_mode='HTML'
        )
        return True
    except TelegramError as e:
        logger.error(f"Ошибка Telegram при отправке изображения: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке изображения: {e}")
        return False


async def send_image_with_fallback(chat_id, question_num, question_data, context):
    """Отправляет изображение с резервным вариантом"""
    image_url = question_data.get('image_url')

    if not image_url:
        logger.error(f"URL изображения не указан для вопроса {question_num}")
        return False

    # Пробуем отправить изображение по URL
    success = await send_image_from_url(
        chat_id=chat_id,
        image_url=image_url,
        caption=f"{question_data['question']}\n\nВведите ваш ответ:",
        context=context
    )

    if not success:
        # Если не удалось, используем текстовую альтернативу
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Не удалось загрузить изображение. 😢\n\n{question_data['question']}\n\nВведите ваш ответ:",
            reply_markup=get_main_keyboard()
        )
        return False

    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    if user_id not in user_data:
        user_data[user_id] = {
            'answered_questions': [],
            'hints_collected': [],
            'awaiting_input': None
        }

    # Если это сообщение (не callback)
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())
    # Если это callback (нажатие кнопки)
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=get_main_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == 'info':
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_keyboard()
        )

    elif query.data == 'enter_password':
        user_data[user_id]['awaiting_input'] = 'password'
        await query.edit_message_text(
            "🔒 Введите пароль:",
            reply_markup=get_main_keyboard()
        )

    elif query.data == 'start_quest':
        available_questions = [i for i in range(len(QUESTIONS))
                               if i not in user_data[user_id]['answered_questions']]

        if not available_questions:
            await query.edit_message_text(
                "Вы уже ответили на все вопросы! 🥳🥳🥳.\nПереходите к вводу пароля.",
                reply_markup=get_main_keyboard()
            )
            return

        question_num = random.choice(available_questions)
        question_data = QUESTIONS[question_num]
        user_data[user_id]['awaiting_input'] = f'question_{question_num}'

        if question_data['type'] == 'text':
            await query.edit_message_text(
                f"{question_data['question']}\n\nВведите ваш ответ:",
                reply_markup=get_main_keyboard()
            )

        elif question_data['type'] == 'image':
            # Изменяем сообщение с кнопкой
            await query.edit_message_text(
                "Загружаю изображение с заданием...",
                reply_markup=get_main_keyboard()
            )

            # Отправляем изображение отдельным сообщением
            await send_image_with_fallback(
                chat_id=query.message.chat_id,
                question_num=question_num,
                question_data=question_data,
                context=context
            )

    elif query.data == 'progress':
        hints = user_data[user_id]['hints_collected']
        if hints:
            hints_text = "🗝️ Вы собрали следующие буквы:\n" + \
                " ".join(sorted(hints))
        else:
            hints_text = "Вы еще не собрали ни одной буквы."

        total_answered = len(user_data[user_id]['answered_questions'])
        progress_text = f"Отвечено вопросов: {total_answered}/4\n\n{hints_text}"
        await query.edit_message_text(progress_text, reply_markup=get_main_keyboard())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_input = update.message.text.strip().lower()

    if user_id not in user_data:
        await start(update, context)
        return

    if user_data[user_id]['awaiting_input'] == 'password':
        if user_input == CORRECT_PASSWORD.lower():
            response = '''✅ Пароль верный! 🥳🎉🥳.
            \nПоздравляю, ты заслужила свой подарок 😉.
            \nНапиши мне лично, чтобы я мы могли договориться о месте и времени передачи 🎅.
            \nМой ТГ: @not_data_user
        '''
        else:
            response = "❌ Неверный пароль. Попробуй еще раз."

        user_data[user_id]['awaiting_input'] = None
        await update.message.reply_text(response, reply_markup=get_main_keyboard())

    elif user_data[user_id]['awaiting_input'] and user_data[user_id]['awaiting_input'].startswith('question_'):
        question_num = int(user_data[user_id]['awaiting_input'].split('_')[1])
        question_data = QUESTIONS[question_num]

        if user_input == question_data['answer'].lower():
            user_data[user_id]['answered_questions'].append(question_num)

            if question_num in HINTS:
                hint = HINTS[question_num]
                user_data[user_id]['hints_collected'].append(hint)
                response = f"✅ Правильно! Вы получаете букву: {hint}"
            else:
                response = "✅ Правильно!"
        else:
            response = "❌ Неправильно. Попробуйте еще раз."

        user_data[user_id]['awaiting_input'] = None
        await update.message.reply_text(response, reply_markup=get_main_keyboard())

    else:
        await update.message.reply_text(
            "Я не знаю такой команды. Пожалуйста, используй только кнопки ниже:",
            reply_markup=get_main_keyboard()
        )


def get_main_keyboard():
    """Создает основную клавиатуру"""
    keyboard = [
        [InlineKeyboardButton("Инфо", callback_data='info')],
        [InlineKeyboardButton("Начать квест", callback_data='start_quest')],
        [InlineKeyboardButton(
            "Ввести пароль", callback_data='enter_password')],
        [InlineKeyboardButton("Прогресс", callback_data='progress')]
    ]
    return InlineKeyboardMarkup(keyboard)


def main():
    """Основная функция запуска бота"""
    TOKEN = ""

    # Создаем приложение с настройками
    application = Application.builder()\
        .token(TOKEN)\
        .read_timeout(30)\
        .write_timeout(30)\
        .connect_timeout(30)\
        .pool_timeout(30)\
        .build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        timeout=30
    )


if __name__ == "__main__":
    main()
