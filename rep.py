import os
import shutil
from datetime import datetime

# --- ШАГ 1: БЭКАП ---
# Создаем уникальную папку для бэкапа, чтобы не перезаписать старые
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = f'backup_before_fix_{timestamp}'
os.makedirs(backup_dir, exist_ok=True)

print(f"--- Создаю бэкап в папку: {backup_dir} ---")

# Карта замен (MacCyrillic байт -> UTF-8 буква)
mapping = {
    0x80: 'А', 0x81: 'Б', 0x82: 'В', 0x83: 'Г', 0x84: 'Д', 0x85: 'Е', 0x86: 'Ж', 0x87: 'З',
    0x88: 'И', 0x89: 'Й', 0x8a: 'К', 0x8b: 'Л', 0x8c: 'М', 0x8d: 'Н', 0x8e: 'О', 0x8f: 'П',
    0x90: 'Р', 0x91: 'С', 0x92: 'Т', 0x93: 'У', 0x94: 'Ф', 0x95: 'Х', 0x96: 'Ц', 0x97: 'Ч',
    0x98: 'Ш', 0x99: 'Щ', 0x9a: 'Ъ', 0x9b: 'Ы', 0x9c: 'Ь', 0x9d: 'Э', 0x9e: 'Ю', 0x9f: 'Я',
    0xa0: 'а', 0xa1: 'б', 0xa2: 'в', 0xa3: 'г', 0xa4: 'д', 0xa5: 'е', 0xa6: 'ж', 0xa7: 'з',
    0xa8: 'и', 0xa9: 'й', 0xaa: 'к', 0xab: 'л', 0xac: 'м', 0xad: 'н', 0xae: 'о', 0xaf: 'п',
    0xe0: 'р', 0xe1: 'с', 0xe2: 'т', 0xe3: 'у', 0xe4: 'ф', 0xe5: 'х', 0xe6: 'ц', 0xe7: 'ч',
    0xe8: 'ш', 0xe9: 'щ', 0xea: 'ъ', 0xeb: 'ы', 0xec: 'ь', 0xed: 'э', 0xee: 'ю', 0xef: 'я',
    0xdd: 'Ё', 0xde: 'ё'
}

def is_utf8_start(byte):
    """Проверяет, является ли байт началом многобайтовой последовательности UTF-8"""
    return (byte & 0b11100000) == 0b11000000 or \
           (byte & 0b11110000) == 0b11100000 or \
           (byte & 0b11111000) == 0b11110000

def get_utf8_length(byte):
    """Определяет длину UTF-8 символа по первому байту"""
    if (byte & 0b11100000) == 0b11000000: return 2
    if (byte & 0b11110000) == 0b11100000: return 3
    if (byte & 0b11111000) == 0b11110000: return 4
    return 1

def process_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    new_data = bytearray()
    i = 0
    total_len = len(data)
    
    while i < total_len:
        byte = data[i]
        
        # 1. Если это ASCII (английские буквы, команды \, скобки и т.д.) - пропускаем как есть
        if byte < 0x80:
            new_data.append(byte)
            i += 1
            continue
            
        # 2. Если это начало валидного UTF-8 символа
        if is_utf8_start(byte):
            length = get_utf8_length(byte)
            # Проверяем, не битая ли последовательность
            chunk = data[i : i + length]
            try:
                chunk.decode('utf-8') # Проверка на валидность
                new_data.extend(chunk) # Если ок - сохраняем целиком
                i += length
                continue
            except UnicodeDecodeError:
                pass # Если не валидный UTF-8, идем к замене по мапе
        
        # 3. Если это одиночный "битый" байт из нашего списка MacCyrillic
        if byte in mapping:
            fixed_char = mapping[byte]
            new_data.extend(fixed_char.encode('utf-8'))
            i += 1
        else:
            # Если байт вообще непонятный - оставляем как есть
            new_data.append(byte)
            i += 1
            
    with open(filepath, 'wb') as f:
        f.write(new_data)

# Проходим по всем файлам
for filename in os.listdir('.'):
    if filename.endswith('.tex'):
        # Сначала копируем в бэкап
        shutil.copy2(filename, os.path.join(backup_dir, filename))
        
        # Потом лечим оригинал (кроме основного файла, если он чистый)
        if filename != 'main.tex':
            print(f"Лечу файл: {filename}")
            process_file(filename)

print(f"\n--- ГОТОВО ---")
print(f"Все оригиналы сохранены в папке: {backup_dir}")