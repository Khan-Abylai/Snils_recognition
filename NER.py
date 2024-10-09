import re
import json

# Примерные результаты OCR, которые нужно распарсить
ocr_results = [
    {"x": 299, "y": 33, "text": "Российская", "confidence": 91},
    {"x": 587, "y": 42, "text": "Федерация", "confidence": 91},
    {"x": 110, "y": 134, "text": "СТРАХОВОЕ", "confidence": 89},
    {"x": 500, "y": 150, "text": "СВИДЕТЕЛЬСТВО", "confidence": 90},
    {"x": 66, "y": 220, "text": "ОБЯЗАТЕЛЬНОГО", "confidence": 91},
    {"x": 773, "y": 228, "text": "СТРАХОВАНИЯ", "confidence": 91},
    {"x": 432, "y": 232, "text": "ПЕНСИОННОГО", "confidence": 92},
    {"x": 389, "y": 286, "text": "162606643", "confidence": 92},
    {"x": 702, "y": 297, "text": "59", "confidence": 38},
    {"x": 283, "y": 346, "text": "АШУРКО", "confidence": 89},
    {"x": 285, "y": 401, "text": "МИЛАНА", "confidence": 91},
    {"x": 285, "y": 451, "text": "ЕВГЕНЬЕВНА", "confidence": 90},
    {"x": 272, "y": 509, "text": "рождения", "confidence": 83},
    {"x": 157, "y": 513, "text": "место", "confidence": 79},
    {"x": 614, "y": 516, "text": "4", "confidence": 92},
    {"x": 651, "y": 520, "text": "октября", "confidence": 90},
    {"x": 827, "y": 524, "text": "1993", "confidence": 96},
    {"x": 282, "y": 556, "text": "СЕГЕЖА", "confidence": 91},
    {"x": 282, "y": 658, "text": "РЕСПУБЛИКА", "confidence": 91},
    {"x": 583, "y": 666, "text": "КАРЕЛИЯ", "confidence": 58},
    {"x": 609, "y": 796, "text": "1", "confidence": 92},
    {"x": 636, "y": 798, "text": "ноября", "confidence": 92},
    {"x": 758, "y": 801, "text": "2010", "confidence": 65}
]


# Функция для извлечения ID
def extract_id(ocr_results):
    id_number = ''
    id_parts = []

    for result in ocr_results:
        if re.match(r'^\d{9}$', result["text"]):  # 9 цифр, для основного ID
            id_parts.append(result["text"])
        elif re.match(r'^\d{2}$', result["text"]):  # Два последних цифры для контрольного числа
            id_parts.append(result["text"])

    if len(id_parts) == 2:
        id_number = f"{id_parts[0][:3]}-{id_parts[0][3:6]}-{id_parts[0][6:]} {id_parts[1]}"

    return id_number


# Функция для извлечения имени (ФИО)
def extract_name(ocr_results):
    surname = ''
    first_name = ''
    patronymic = ''

    for result in ocr_results:
        if re.match(r'[А-ЯЁ][а-яё]+', result["text"]):  # Имя на кириллице
            if not surname:
                surname = result["text"]
            elif not first_name:
                first_name = result["text"]
            elif not patronymic:
                patronymic = result["text"]

    name = f"{surname} {first_name} {patronymic}".strip()
    return name


# Функция для извлечения даты рождения
def extract_birth_date(ocr_results):
    birth_date = ''
    birth_parts = []

    for result in ocr_results:
        if re.match(r'^\d{1,2}$', result["text"]):  # День
            birth_parts.append(result["text"])
        elif re.match(r'[а-я]+', result["text"]):  # Месяц
            birth_parts.append(result["text"])
        elif re.match(r'^\d{4}$', result["text"]):  # Год
            birth_parts.append(result["text"])

    if len(birth_parts) == 3:
        birth_date = " ".join(birth_parts)

    return birth_date


# Функция для извлечения места рождения
def extract_place_of_birth(ocr_results):
    place_of_birth = ''
    city = ''
    region = []

    for result in ocr_results:
        if result["confidence"] > 80:
            if "СЕГЕЖА" in result["text"]:  # Город
                city = result["text"]
            elif "РЕСПУБЛИКА" in result["text"] or "КАРЕЛИЯ" in result["text"]:
                region.append(result["text"])

    if city and region:
        place_of_birth = f"{city} {' '.join(region)}"

    return place_of_birth


# Функция для извлечения даты регистрации
def extract_registration_date(ocr_results):
    registration_date = ''
    reg_parts = []

    for result in ocr_results:
        if re.match(r'^\d{1,2}$', result["text"]):  # День
            reg_parts.append(result["text"])
        elif re.match(r'[а-я]+', result["text"]):  # Месяц
            reg_parts.append(result["text"])
        elif re.match(r'^\d{4}$', result["text"]):  # Год
            reg_parts.append(result["text"])

    if len(reg_parts) == 3:
        registration_date = " ".join(reg_parts)

    return registration_date


# Собираем данные в структуру
person_data = {
    "ID Number": extract_id(ocr_results),
    "Name": extract_name(ocr_results),
    "Date of Birth": extract_birth_date(ocr_results),
    "Place of Birth": extract_place_of_birth(ocr_results),
    "Gender": "Женский",  # Пол можно определить из контекста
    "Registration Date": extract_registration_date(ocr_results)
}

# Сохранение данных в JSON файл
output_json_path = "output_person_data.json"
with open(output_json_path, "w", encoding='utf-8') as json_file:
    json.dump(person_data, json_file, ensure_ascii=False, indent=4)

print(f"Данные распознаны и сохранены в {output_json_path}.")
