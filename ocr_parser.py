
import easyocr
from PIL import Image
import pandas as pd
import re

# === Путь к изображению ===
image_path = "image.png"  # замените на ваш путь к файлу

# === OCR с EasyOCR ===
reader = easyocr.Reader(['ru', 'en'], gpu=False)
results = reader.readtext(image_path)

# === Чтение строк ===
lines = [line[1].strip() for line in results if line[1].strip()]

# === Парсинг данных ===
records = []
current = {}
id_pattern = re.compile(r'\d{6,}')

for line in lines:
    if id_pattern.search(line):
        if current:
            records.append(current)
        id_val = id_pattern.search(line).group()
        name_val = line.replace(id_val, "").strip()
        current = {"ID": id_val, "Имя": name_val}
    elif any(word in line.lower() for word in ["округ", "г.о.", "посёлок", "ул.", "д.", "кв."]):
        current["Адрес"] = line
    elif "Имя" not in current and any(c.isalpha() for c in line):
        current["Имя"] = line

if current:
    records.append(current)

# === Формирование таблицы ===
df = pd.DataFrame(records, columns=["ID", "Имя", "Адрес"])

# === Сохранение в Excel ===
df.to_excel("распознанные_данные.xlsx", index=False)

print("✅ Готово! Данные сохранены в 'распознанные_данные.xlsx'")
