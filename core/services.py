import os

import httpx
from bs4 import BeautifulSoup

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
    schools_url = await database.get_json_data()
    for i in range(0, 582):
        school_url = schools_url[i][str(i + 1)]

        url = f"https://{school_url}/o-nas/pedagogicheskii-sostav#"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            teacher_links = soup.find_all("a", class_="fio")
            teacher_url_list = [
                "https://" + school_url + link.get("href") for link in teacher_links
            ]
            await database.create_json_data_2(i + 1, teacher_url_list)
            print(f"Школа {i + 1}/581")
        else:
            print(f"Error:\n{response.status_code}")


async def get_teachers_info():
    schools_url = await database.get_json_data()
    teachers_url = await database.get_json_data_2()
    #todo: загрузить профиль сотрудника и через суп спарсить данные, потом сохранить
