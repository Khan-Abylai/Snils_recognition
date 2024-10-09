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

# Список слов для игнорирования (без привязки к координатам)
ignore_words = [
    "российская",
    "федерация",
    "страховое",
    "свидетельство",
    "обязательного",
    "страхования",
    "пенсионного",
    "рождения",
    "место"
]

# Приведение слова к стандартному формату (нижний регистр и без знаков препинания)
def clean_and_format_word(word):
    return re.sub(r'\W+', '', word).lower()  # Убираем знаки и приводим к нижнему регистру

# Проверка, нужно ли игнорировать слово
def is_ignored(word):
    formatted_word = clean_and_format_word(word)
    return formatted_word in ignore_words

# Фильтрация символов для удаления знаков препинания и символов
def clean_word(word):
    return re.sub(r'\W+', '', word)  # Убираем всё, кроме букв и цифр

# Проверка, является ли строка числом
def is_number(word):
    return word.isdigit()

# Проверка, содержит ли слово только буквы (не цифры)
def is_alpha(word):
    return word.isalpha()

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
        # Игнорируем слова из списка ignore_words
        if not is_ignored(word):
            # Если слово состоит более чем из одной буквы или это цифра, добавляем его
            if len(word) > 1 or is_number(word):
                ocr_results.append((x, y, word, conf, "text"))

# Сохранение исходных результатов OCR перед группировкой
txt_output_path_raw = "ocr_results_raw.txt"

try:
    with open(txt_output_path_raw, "w", encoding="utf-8") as file:
        for item in ocr_results:
            file.write(f"x: {item[0]}, y: {item[1]}, text: {item[2]}, confidence: {item[3]}, ocr_type: {item[4]}\n")
    print(f"Изначальные результаты OCR сохранены в {txt_output_path_raw}")
except Exception as e:
    print(f"Ошибка при сохранении файла: {e}")

# Функция для группировки близко расположенных результатов с учетом игнорирования цифр при группировке имен
def group_nearby_results(results, x_threshold=50, y_threshold=30):
    grouped_results = []
    current_group = []

    for i, (x, y, word, conf, ocr_type) in enumerate(results):
        if not current_group:
            current_group.append((x, y, word, conf, ocr_type))
        else:
            last_x, last_y, last_word, _, _ = current_group[-1]

            # Проверяем близость текущего элемента к последнему в текущей группе
            if abs(x - last_x) < x_threshold or abs(y - last_y) < y_threshold:
                # Если текущее слово содержит цифры, и группа состоит из букв, не добавляем в группу
                if is_alpha(last_word) and is_number(word):
                    continue
                # Если текущее слово содержит буквы, и группа состоит из цифр, не добавляем в группу
                if is_number(last_word) and is_alpha(word):
                    continue
                current_group.append((x, y, word, conf, ocr_type))
            else:
                # Заканчиваем текущую группу и начинаем новую
                grouped_results.append(current_group)
                current_group = [(x, y, word, conf, ocr_type)]

    # Добавляем последнюю группу, если она существует
    if current_group:
        grouped_results.append(current_group)

    return grouped_results

# Сортировка результатов по y, затем по x координатам
ocr_results_sorted = sorted(ocr_results, key=lambda k: (k[1], k[0]))

# Группировка результатов
grouped_ocr_results = group_nearby_results(ocr_results_sorted)

# Сохранение отсортированных и сгруппированных результатов в текстовый файл
txt_output_path_grouped = "ocr_results_grouped.txt"

try:
    with open(txt_output_path_grouped, "w", encoding="utf-8") as file:
        for group in grouped_ocr_results:
            grouped_text = ' '.join([item[2] for item in group])  # Объединяем текст группы в строку
            x_coords = [item[0] for item in group]
            y_coords = [item[1] for item in group]
            confs = [item[3] for item in group]
            file.write(f"x: {min(x_coords)}, y: {min(y_coords)}, text: {grouped_text}, confidence: {min(confs)}, ocr_type: text\n")
    print(f"Сгруппированные результаты OCR сохранены в {txt_output_path_grouped}")
except Exception as e:
    print(f"Ошибка при сохранении файла: {e}")
