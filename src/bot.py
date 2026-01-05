# bot.py
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackQueryHandler

from config import *
# bot.py (частично)
from handlers.main import start, get_info, handle_main_menu
from handlers.progress_handler import start_quest, show_progress, reset_progress, check_final_password
from handlers.level1_handler import start_level1, handle_level1_answer
from handlers.level2_handler import start_level2, check_level2_answer
from handlers.level3_handler import start_level3, check_level3_answer
from handlers.level4_handler import start_level4, check_level4_answer

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Основная функция запуска бота"""
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
                MessageHandler(filters.Regex('^🚀 Начать квест$'), start_quest),
                MessageHandler(filters.Regex('^ℹ️ Информация$'), get_info),
                MessageHandler(filters.Regex('^📊 Мой прогресс$'), show_progress),
                MessageHandler(filters.Regex('^🔄 Сбросить прогресс$'), reset_progress),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
            ],
            LEVEL_1_MULTIPLE_CHOICE: [
                CallbackQueryHandler(handle_level1_answer, pattern='^level1_')
            ],
            LEVEL_2_ASSOCIATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_level2_answer)
            ],
            LEVEL_3_CAESAR_CIPHER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_level3_answer)
            ],
            LEVEL_4_FIND_ANIMAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_level4_answer)
            ],
            ENTER_FINAL_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_final_password)
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )
    
    # Добавление обработчика
    application.add_handler(conv_handler)
    
    # Запуск бота
    logger.info("Бот запущен...")
    logger.info(f"Папка с данными: {DATA_DIR}")
    logger.info(f"Папка с изображениями: {IMG_DIR}")
    
    application.run_polling()

if __name__ == '__main__':
    main()