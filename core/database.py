import csv
import datetime
import json
import os


root_directory = os.getcwd()

file_name = "data.json"
file_path = os.path.join(root_directory, file_name)

file_name_2 = "data_2.json"
file_2_path = os.path.join(root_directory, file_name_2)

file_name_3 = "data_3.json"
file_3_path = os.path.join(root_directory, file_name_3)

file_name_4 = "data_4.json"
file_4_path = os.path.join(root_directory, file_name_4)

headers = ["ФИО", "Должность", "Школа", "Ссылка", "Окончил МПГУ", "Употребляются МПГУ"]

file_name_5 = "data_5.csv"
file_5_path = os.path.join(root_directory, file_name_5)


async def create_json_data(school_id: int, website: str) -> None:
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []

    data.append({school_id: website})

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


async def get_json_data() -> list:
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


async def create_json_data_2(school_id: int, teacher_cards: list) -> None:
    try:
        with open(file_2_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append({school_id: teacher_cards})

    with open(file_2_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


async def get_json_data_2() -> list:
    with open(file_2_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


async def create_json_data_3(incoming_data: dict) -> None:
    try:
        with open(file_3_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(incoming_data)

    with open(file_3_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


async def get_json_data_3() -> list:
    with open(file_3_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


async def create_json_data_4(incoming_data: str) -> None:
    try:
        with open(file_4_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(incoming_data)

    with open(file_4_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


async def create_csv_data(incoming_data: list) -> None:
    file_exists = os.path.exists(file_5_path)

    with open(file_5_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(headers)

        try:
            writer.writerows(incoming_data)
        except Exception as error:
            print(f"{datetime.datetime.now()}")
            print(f"Произошла ошибка при добавлении данных{error}")
