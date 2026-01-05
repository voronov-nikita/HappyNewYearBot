# utils/cipher.py

def caesar_cipher(text: str, shift: int) -> str:
    """Шифрование/дешифрование текста шифром Цезаря для русского алфавита"""
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                # Русские заглавные буквы
                if 'А' <= char <= 'Я':
                    result += chr((ord(char) + shift - 1040) % 32 + 1040)
                # Английские заглавные буквы
                elif 'A' <= char <= 'Z':
                    result += chr((ord(char) + shift - 65) % 26 + 65)
                else:
                    result += char
            else:
                # Русские строчные буквы
                if 'а' <= char <= 'я':
                    result += chr((ord(char) + shift - 1072) % 32 + 1072)
                # Английские строчные буквы
                elif 'a' <= char <= 'z':
                    result += chr((ord(char) + shift - 97) % 26 + 97)
                else:
                    result += char
        else:
            result += char
    return result