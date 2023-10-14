import os

import httpx

from core import database


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
                await database.create_json_data(counter, website)
                counter += 1
        else:
            print(f"Error:\n{response.status_code}")


async def get_teachers_urls():
    teachers_url = await database.get_json_data()
    for i in range(581):
        print(teachers_url[i])
