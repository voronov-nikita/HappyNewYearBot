# utils/file_loader.py
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple
from config import (
    DATA_DIR, QUESTIONS_FILE, ASSOCIATIONS_FILE, ANIMALS_FILE,
    CAESAR_TEXT_FILE, CAESAR_ANSWER_FILE,
    EXAMPLE_QUESTIONS, EXAMPLE_ASSOCIATIONS, EXAMPLE_ANIMALS,
    CAESAR_SAMPLE_TEXT, CAESAR_SAMPLE_ANSWER
)

def ensure_data_dir():
    """Создание папки data, если её нет"""
    DATA_DIR.mkdir(exist_ok=True)

def load_questions() -> List[Dict]:
    """Загрузка вопросов про Азию из JSON файла"""
    ensure_data_dir()
    
    if not QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(EXAMPLE_QUESTIONS, f, indent=2, ensure_ascii=False)
    
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_random_question() -> Tuple[Dict, int]:
    """Получение случайного вопроса про Азию"""
    questions = load_questions()
    question_index = random.randint(0, len(questions) - 1)
    return questions[question_index], question_index

def load_associations() -> List[Dict]:
    """Загрузка ассоциаций из JSON файла"""
    ensure_data_dir()
    
    if not ASSOCIATIONS_FILE.exists():
        with open(ASSOCIATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(EXAMPLE_ASSOCIATIONS, f, indent=2, ensure_ascii=False)
    
    with open(ASSOCIATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_random_association() -> Tuple[str, str]:
    """Получение случайного изображения для ассоциации и правильного ответа"""
    associations = load_associations()
    selected = random.choice(associations)
    return selected["image"], selected["answer"]

def load_animals() -> List[Dict]:
    """Загрузка животных из JSON файла"""
    ensure_data_dir()
    
    if not ANIMALS_FILE.exists():
        with open(ANIMALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(EXAMPLE_ANIMALS, f, indent=2, ensure_ascii=False)
    
    with open(ANIMALS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_random_animal() -> Tuple[str, str]:
    """Получение изображения с животным и правильного ответа"""
    animals = load_animals()
    selected = random.choice(animals)
    return selected["image"], selected["answer"]

def load_caesar_data() -> Tuple[str, str, str]:
    """Загрузка данных для шифра Цезаря"""
    ensure_data_dir()
    
    from utils.cipher import caesar_cipher
    
    # Если файла нет, создаем пример
    if not CAESAR_TEXT_FILE.exists():
        with open(CAESAR_TEXT_FILE, 'w', encoding='utf-8') as f:
            encrypted_text = caesar_cipher(CAESAR_SAMPLE_TEXT, 3)
            f.write(encrypted_text)
    
    # Если файла с ответом нет, создаем
    if not CAESAR_ANSWER_FILE.exists():
        with open(CAESAR_ANSWER_FILE, 'w', encoding='utf-8') as f:
            f.write(CAESAR_SAMPLE_ANSWER)
    
    # Читаем зашифрованный текст
    with open(CAESAR_TEXT_FILE, 'r', encoding='utf-8') as f:
        encrypted_text = f.read()
    
    # Читаем ответ
    with open(CAESAR_ANSWER_FILE, 'r', encoding='utf-8') as f:
        correct_answer = f.read().strip()
    
    # Расшифровываем текст для отображения (со смещением -3)
    decrypted_text = caesar_cipher(encrypted_text, -3)
    
    return encrypted_text, decrypted_text, correct_answer