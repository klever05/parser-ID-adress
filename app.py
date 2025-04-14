
import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Распознавание карточек", layout="centered")

st.title("🧾 Распознавание карточек с ID, Именем и Адресом")

# Загрузка изображения
uploaded_file = st.file_uploader("Загрузите изображение (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Загруженное изображение", use_column_width=True)

    # OCR
    st.info("📤 Распознаём текст...")
    text = pytesseract.image_to_string(image, lang="rus+eng")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Парсинг карточек
    records = []
    current = {}
    id_pattern = re.compile(r'\d{6,}')  # ID = 6+ цифр

    for line in lines:
        if id_pattern.search(line):
            if current:
                records.append(current)
            match = id_pattern.search(line)
            id_val = match.group()
            name_val = line.replace(id_val, "").strip()
            current = {"ID": id_val, "Имя": name_val}
        elif any(word in line.lower() for word in ["округ", "г.о.", "посёлок", "д.", "ул.", "кв."]):
            current["Адрес"] = line
        elif "Имя" not in current and any(c.isalpha() for c in line):
            current["Имя"] = line

    if current:
        records.append(current)

    if records:
        df = pd.DataFrame(records, columns=["ID", "Имя", "Адрес"])
        st.success("✅ Готово! Вот таблица:")
        st.dataframe(df)

        # Скачивание
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Скачать Excel-файл",
            data=output.getvalue(),
            file_name="распознанные_данные.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Не удалось распознать данные. Проверь изображение.")
