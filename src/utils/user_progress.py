# utils/user_progress.py
import json
import logging
from typing import Dict
from config import USER_PROGRESS_FILE, DATA_DIR

logger = logging.getLogger(__name__)


class UserProgress:
    def __init__(self):
        self.progress_file = USER_PROGRESS_FILE
        self.progress = self.load_progress()

    def load_progress(self) -> Dict:
        """Загрузка прогресса пользователей из файла"""
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(exist_ok=True)

        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Проверяем, не пустой ли файл
                        return json.loads(content)
                    else:
                        logger.warning(
                            f"Файл {self.progress_file} пустой. Создаю новый.")
                        return {}
            except json.JSONDecodeError as e:
                logger.error(
                    f"Ошибка при чтении файла {self.progress_file}: {e}")
                logger.info("Создаю новый файл с прогрессом.")
                return {}
            except Exception as e:
                logger.error(f"Ошибка при загрузке прогресса: {e}")
                return {}
        else:
            logger.info(
                f"Файл {self.progress_file} не существует. Создаю новый.")
            return {}

    def save_progress(self):
        """Сохранение прогресса пользователей в файл"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка при сохранении прогресса: {e}")

    def get_user_progress(self, user_id: int) -> Dict:
        """Получение прогресса пользователя"""
        user_id_str = str(user_id)
        if user_id_str not in self.progress:
            self.progress[user_id_str] = {
                "level1_completed": False,
                "level2_completed": False,
                "level3_completed": False,
                "level4_completed": False,
                "current_level": 1,
                "hints_collected": 0
            }
            self.save_progress()  # Сохраняем нового пользователя
        return self.progress[user_id_str]

    # utils/user_progress.py (проверьте этот метод)


    def update_level_completion(self, user_id: int, level: int):
        """Обновление прогресса после прохождения уровня"""
        user_id_str = str(user_id)
        self.get_user_progress(user_id)  # Ensure user exists

        if level == 1:
            self.progress[user_id_str]["level1_completed"] = True
            self.progress[user_id_str]["current_level"] = 2
            self.progress[user_id_str]["hints_collected"] = 1
        elif level == 2:
            self.progress[user_id_str]["level2_completed"] = True
            self.progress[user_id_str]["current_level"] = 3
            self.progress[user_id_str]["hints_collected"] = 2
        elif level == 3:
            self.progress[user_id_str]["level3_completed"] = True
            self.progress[user_id_str]["current_level"] = 4
            self.progress[user_id_str]["hints_collected"] = 3
        elif level == 4:
            self.progress[user_id_str]["level4_completed"] = True
            self.progress[user_id_str]["hints_collected"] = 4

        self.save_progress()  # Не забудьте сохранить!
        logger.info(f"Пользователь {user_id} прошел уровень {level}")

    def reset_progress(self, user_id: int):
            """Сброс прогресса пользователя"""
            user_id_str = str(user_id)
            self.progress[user_id_str] = {
                "level1_completed": False,
                "level2_completed": False,
                "level3_completed": False,
                "level4_completed": False,
                "current_level": 1,
                "hints_collected": 0
            }
            self.save_progress()
