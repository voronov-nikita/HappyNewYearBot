import logging
import os
from pathlib import Path
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Пути к папкам
BASE_DIR = Path(__file__).parent.parent
IMG_DIR = BASE_DIR / "img"

# Создание папки для изображений, если ее нет
IMG_DIR.mkdir(exist_ok=True)

# Состояния для ConversationHandler
ENTER_PASSWORD = 1
MAIN_MENU = 0

# Настройки пароля и подсказки
PASSWORD = "2024"  # Пароль из 4 символов
HINT = "Этот год был объявлен Годом семьи в России"  # Подсказка
INFO_TEXT = """🎉 Добро пожаловать в бот-поздравление! 🎉

Этот бот создан для праздничного настроения. 
Чтобы получить поздравление, вам нужно угадать пароль из 4 символов.

Используйте кнопки ниже для навигации:
• "Ввести пароль" - попытаться угадать пароль
• "Получить подсказку" - получить помощь
• "Информация" - узнать больше о боте

Удачи! 🍀"""

# Клавиатура
KEYBOARD = [
    ['Ввести пароль', 'Получить подсказку'],
    ['Информация', 'Показать картинку']
]
REPLY_MARKUP = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

# Функция для отправки изображения
async def send_image(update: Update, context: CallbackContext, image_name: str) -> bool:
    """Отправляет изображение из папки img"""
    image_path = IMG_DIR / image_name
    
    if not image_path.exists():
        logger.error(f"Изображение {image_name} не найдено в {IMG_DIR}")
        return False
    
    try:
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo)
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        return False

# Команда /start с изображением
async def start(update: Update, context: CallbackContext) -> int:
    # Отправляем приветственное изображение, если оно есть
    welcome_sent = await send_image(update, context, "welcome.jpg")
    
    text = "Привет! Я бот-поздравление 🎂\n"
    if not welcome_sent:
        text += "🎄🎅🌟\n"  # Добавляем эмодзи, если нет картинки
    
    text += "Чтобы получить поздравление, угадай пароль из 4 символов.\nИспользуй кнопки ниже:"
    
    await update.message.reply_text(text, reply_markup=REPLY_MARKUP)
    return MAIN_MENU

# Обработка кнопки "Ввести пароль"
async def enter_password(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Введите пароль из 4 символов:")
    return ENTER_PASSWORD

# Проверка введенного пароля с отправкой картинки при успехе
async def check_password(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    
    if user_input == PASSWORD:
        # Отправляем поздравление с картинкой
        congrats_sent = await send_image(update, context, "congrats.jpg")
        
        text = "🎊 Поздравляем! Вы угадали пароль! 🎊\n"
        if not congrats_sent:
            text += "🎁✨🎉\n"  # Добавляем эмодзи, если нет картинки
        
        text += "Желаем вам счастья, здоровья и удачи! 🌟\nВозвращайтесь кнопками ниже:"
        
        await update.message.reply_text(text, reply_markup=REPLY_MARKUP)
        return MAIN_MENU
    else:
        await update.message.reply_text(
            "❌ Неверный пароль! Попробуйте еще раз.\n"
            "Введите пароль из 4 символов:"
        )
        return ENTER_PASSWORD

# Обработка кнопки "Получить подсказку" с картинкой
async def get_hint(update: Update, context: CallbackContext) -> int:
    # Отправляем картинку с подсказкой, если есть
    hint_sent = await send_image(update, context, "hint.jpg")
    
    text = f"💡 Подсказка: {HINT}"
    await update.message.reply_text(text, reply_markup=REPLY_MARKUP)
    return MAIN_MENU

# Обработка кнопки "Информация"
async def get_info(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(INFO_TEXT, reply_markup=REPLY_MARKUP)
    return MAIN_MENU

# Обработка кнопки "Показать картинку"
async def show_image(update: Update, context: CallbackContext) -> int:
    # Можно показывать случайную картинку или конкретную
    # Пример: показываем welcome.jpg
    image_sent = await send_image(update, context, "welcome.jpg")
    
    if not image_sent:
        await update.message.reply_text(
            "📷 Картинка не найдена! Добавьте изображения в папку img/\n"
            "Доступные имена: welcome.jpg, congrats.jpg, hint.jpg",
            reply_markup=REPLY_MARKUP
        )
    else:
        await update.message.reply_text(
            "Вот картинка! Используйте кнопки ниже:",
            reply_markup=REPLY_MARKUP
        )
    
    return MAIN_MENU

# Обработка любых других сообщений в основном меню
async def handle_main_menu(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    
    if text == "Ввести пароль":
        return await enter_password(update, context)
    elif text == "Получить подсказку":
        return await get_hint(update, context)
    elif text == "Информация":
        return await get_info(update, context)
    elif text == "Показать картинку":
        return await show_image(update, context)
    else:
        await update.message.reply_text(
            "Используйте кнопки ниже для навигации:",
            reply_markup=REPLY_MARKUP
        )
        return MAIN_MENU

# Команда для админа - проверка доступных картинок
async def check_images(update: Update, context: CallbackContext) -> int:
    admin_id = os.getenv("ADMIN_ID")
    
    if admin_id and str(update.effective_user.id) == admin_id:
        images = list(IMG_DIR.glob("*.jpg")) + list(IMG_DIR.glob("*.png")) + list(IMG_DIR.glob("*.jpeg"))
        
        if images:
            image_list = "\n".join([f"• {img.name}" for img in images])
            await update.message.reply_text(f"📂 Доступные изображения:\n{image_list}")
        else:
            await update.message.reply_text("📂 Папка img/ пуста")
    else:
        await update.message.reply_text("У вас нет прав для этой команды")
    
    return MAIN_MENU

def main() -> None:
    # Получение токена из .env
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        logger.error("Токен бота не найден в .env файле!")
        logger.info("Создайте файл .env с TELEGRAM_BOT_TOKEN=ваш_токен")
        return
    
    # Создание приложения
    application = Application.builder().token(TOKEN).build()
    
    # ConversationHandler для управления состояниями
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex('^Ввести пароль$'), enter_password),
                MessageHandler(filters.Regex('^Получить подсказку$'), get_hint),
                MessageHandler(filters.Regex('^Информация$'), get_info),
                MessageHandler(filters.Regex('^Показать картинку$'), show_image),
                CommandHandler("images", check_images),
                # Обработка любых других сообщений в основном меню
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
            ],
            ENTER_PASSWORD: [
                # Обрабатываем только ввод пароля (любой текст)
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Добавление обработчика
    application.add_handler(conv_handler)
    
    # Запуск бота
    logger.info("Бот запущен...")
    logger.info(f"Папка с изображениями: {IMG_DIR}")
    
    # Проверка существования папки и файлов
    if IMG_DIR.exists():
        logger.info(f"Папка img существует. Содержимое: {list(IMG_DIR.glob('*'))}")
    else:
        logger.warning("Папка img не существует! Создана автоматически.")
    
    application.run_polling()

if __name__ == '__main__':
    main()