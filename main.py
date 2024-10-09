import os
import cv2
import pytesseract
import re

# Указание правильного пути к папке с языковыми моделями
tessdata_dir = "/opt/homebrew/share/tessdata/"
os.environ["TESSDATA_PREFIX"] = tessdata_dir

# Путь к изображению (передается параметром)
image_path = "SNILS.jpg"

# Загрузка изображения
image = cv2.imread(image_path)

# Преобразование в черно-белый формат
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Применение бинаризации Otsu для улучшения распознавания
_, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Конфигурация для распознавания текста (русский)
config_text = '--oem 3 --psm 6 -l rus'

# Фильтрация символов для удаления знаков препинания и символов
def clean_word(word):
    return re.sub(r'\W+', '', word)  # Убираем всё, кроме букв и цифр


# Проверка, является ли строка числом
def is_number(word):
    return word.isdigit()


# Извлечение текстовых данных с бинарного изображения
data_text = pytesseract.image_to_data(binary_image, config=config_text, output_type=pytesseract.Output.DICT)

# Собираем данные в виде списка для сортировки по координатам
ocr_results = []

# Порог для confidence score
confidence_threshold = 10

# Фильтрация текстовых данных (слова и числа)
for i in range(len(data_text['text'])):
    word = clean_word(data_text['text'][i].strip())
    conf = int(data_text['conf'][i]) if data_text['conf'][i] != '-1' else 0
    x, y, w, h = data_text['left'][i], data_text['top'][i], data_text['width'][i], data_text['height'][i]

    # Пропускаем результаты с confidence score ниже заданного порога
    if conf >= confidence_threshold:
        # Если слово состоит более чем из одной буквы или это цифра, добавляем его
        if len(word) > 1 or is_number(word):
            ocr_results.append((x, y, word, conf, "text"))

# Сортировка результатов по y, затем по x координатам
ocr_results_sorted = sorted(ocr_results, key=lambda k: (k[1], k[0]))

# Сохранение отсортированных результатов в текстовый файл
txt_output_path = "ocr_results_sorted.txt"

try:
    with open(txt_output_path, "w", encoding="utf-8") as file:
        for item in ocr_results_sorted:
            file.write(f"x: {item[0]}, y: {item[1]}, text: {item[2]}, confidence: {item[3]}, ocr_type: {item[4]}\n")
    print(f"Результаты OCR сохранены в {txt_output_path}")
except Exception as e:
    print(f"Ошибка при сохранении файла: {e}")
