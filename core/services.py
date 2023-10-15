import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

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


# async def get_teachers_info():
#     teachers_url = await database.get_json_data_2()
#     for teacher_url in teachers_url:
#         for key, value in teacher_url.items():
#             urls_list = value
#             for el in urls_list:
#                 url = el
#                 async with httpx.AsyncClient() as client:
#                     response = await client.get(url)
#
#                 if response.status_code == 200:
#                     html = response.text
#                     soup = BeautifulSoup(html, "html.parser")
#
#                     teacher_div = soup.find("div", class_="panel_teacher groupteachers")
#
#                     title_spans = teacher_div.find_all("span", class_="title")
#
#                     kris_head_div = soup.find("div", class_="kris-component-head")
#                     h1 = kris_head_div.find("h1")
#                     fio = h1.text
#
#                     data_dict = dict()
#
#                     data_dict["ФИО"] = fio
#                     data_dict["Ссылка"] = url
#
#                     for title_span in title_spans:
#                         next_span = title_span.find_next_sibling("span")
#                         if next_span:
#                             title_text = title_span.text
#                             next_text = next_span.text
#                             for char in ["\xa0", "\n", "  "]:
#                                 title_text = title_text.replace(char, "")
#                                 next_text = next_text.replace(char, "")
#
#                             data_dict[title_text] = next_text
#                     await database.create_json_data_3(data_dict)
#                 else:
#                     print(f"Error:\n{response.status_code}")


async def process_url(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            teacher_div = soup.find("div", class_="panel_teacher groupteachers")

            title_spans = teacher_div.find_all("span", class_="title")

            kris_head_div = soup.find("div", class_="kris-component-head")
            h1 = kris_head_div.find("h1")
            fio = h1.text

            data_dict = dict()

            data_dict["ФИО"] = fio
            data_dict["Ссылка"] = url

            for title_span in title_spans:
                next_span = title_span.find_next_sibling("span")
                if next_span:
                    title_text = title_span.text
                    next_text = next_span.text
                    for char in ["\xa0", "\n", "  "]:
                        title_text = title_text.replace(char, "")
                        next_text = next_text.replace(char, "")

                    data_dict[title_text] = next_text
            await database.create_json_data_3(data_dict)
        else:
            print(f"Error for {url}:\n{response.status_code}")
    except Exception as e:
        print(f"Error for {url}:\n{e}")


async def process_batch(urls):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        await asyncio.gather(
            *[
                await loop.run_in_executor(executor, process_url, url)
                for url in urls
            ]
        )


async def get_teachers_info():
    teachers_url = await database.get_json_data_2()
    all_urls = []
    for teacher_data in teachers_url:
        for key, value in teacher_data.items():
            if isinstance(value, list):
                all_urls.extend(value)

    # Разбиваем список URL-ов на пакеты, например, по 100 URL-ов в каждом
    batch_size = 100
    for i in range(0, len(all_urls), batch_size):
        batch = all_urls[i:i + batch_size]
        await process_batch(batch)


async def get_len_json_data():
    teachers = await database.get_json_data_3()
    print(len(teachers))