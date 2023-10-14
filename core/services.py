import json
import os

import httpx


async def create_json_data(email_id: int, website: str) -> None:
    try:
        with open("data.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []

    data.append({"id": email_id, "website": website})

    with open("data.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


async def get_schools_urls():
    counter = 1
    for i in range(1, 60):
        base_url = os.getenv("BASE_URL")
        url = f"{base_url}{i}"
        headers = {"Accept": "application.json"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            for j in range(0, 10):
                website = data["Result"][j]["Cells"]["WebSite"]
                print(f"{counter}: {website}")
                await create_json_data(counter, website)
                counter += 1
        else:
            print(f"Error:\n{response.status_code}")
