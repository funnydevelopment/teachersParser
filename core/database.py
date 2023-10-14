import json


async def create_json_data(school_id: int, website: str) -> None:
    try:
        with open("../data.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []

    data.append({school_id: website})

    with open("../data.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


async def get_json_data() -> list:
    with open("../data.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data
