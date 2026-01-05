# utils/image_sender.py
import logging
from telegram import Update
from telegram.ext import CallbackContext
from config import IMG_DIR

logger = logging.getLogger(__name__)

async def send_image(update: Update, context: CallbackContext, image_name: str) -> bool:
    """Отправка изображения"""
    image_path = IMG_DIR / image_name
    
    # Если изображения нет в папке, используем заглушку
    if not image_path.exists():
        logger.warning(f"Изображение {image_name} не найдено в {IMG_DIR}")
        await update.message.reply_text(f"🖼️ [Изображение: {image_name}]")
        return True
    
    try:
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo)
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await update.message.reply_text(f"🖼️ [Изображение: {image_name}]")
        return True