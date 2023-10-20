import asyncio
import datetime
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
                next_sibling = title_span.find_next_sibling(["span", "a"])
                if next_sibling:
                    title_text = title_span.text
                    next_text = next_sibling.text

                    for char in ["\xa0", "\n", "  "]:
                        title_text = title_text.replace(char, "")
                        next_text = next_text.replace(char, "")

                    if next_sibling.name == "a":
                        email_title = next_sibling["href"]
                    else:
                        email_title = title_text

                    data_dict[email_title] = next_text

            await database.create_json_data_3(data_dict)
        else:
            print(
                f"{datetime.datetime.now()}\nTry error for {url}:{response.status_code}"
            )
            await database.create_json_data_4(url)

    except Exception as e:
        print(f"{datetime.datetime.now()}\nException error for {url}:\n{e}")
        await database.create_json_data_4(url)


async def process_batch(urls):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        await asyncio.gather(
            *[await loop.run_in_executor(executor, process_url, url) for url in urls]
        )


async def get_teachers_info():
    teachers_url = await database.get_json_data_2()
    all_urls = []
    for teacher_data in teachers_url:
        for key, value in teacher_data.items():
            if isinstance(value, list):
                all_urls.extend(value)

    batch_size = 100
    for i in range(0, len(all_urls), batch_size):
        batch = all_urls[i: i + batch_size]
        await process_batch(batch)


async def check_graduate(row: dict) -> bool:
    check_list = [os.getenv("CHECK_WORD_1"), os.getenv("CHECK_WORD_2")]
    check_word = os.getenv("CHECK_WORD_3")
    if check_word in row:
        if row[check_word].lower() in check_list:
            return True
    return False


async def check_is_related(row: dict) -> bool:
    check_list = [os.getenv("CHECK_WORD_1"), os.getenv("CHECK_WORD_2")]
    for key, value in row.items():
        if value.lower() in check_list:
            return True
    return False


async def get_email(row: dict) -> str | None:
    for key, value in row.items():
        if key[0:4] == "mail":
            return value
    return None


async def get_personal_data():
    data = await database.get_json_data_3()

    for row in data:
        data_list = []

        full_name = row["ФИО"]
        data_list.append(full_name)

        try:
            job_title = row["Занимаемая должность (должности):"]
        except KeyError:
            job_title = " "
            print("Такого ключа 'Занимаемая должность (должности)' не существует")
        data_list.append(job_title)

        try:
            work_place = row["Фактическое место работы"]
        except KeyError:
            work_place = " "
            print("Такого ключа 'Фактическое место работы' не существует")
        data_list.append(work_place)

        link = row["Ссылка"]
        data_list.append(link)

        email = await get_email(row)
        if email:
            data_list.append(email)
        else:
            data_list.append(" ")

        graduate = await check_graduate(row)
        data_list.append(graduate)

        is_related = await check_is_related(row)
        data_list.append(is_related)

        data_to_write = [data_list]

        try:
            await database.create_csv_data(data_to_write)
        except Exception as error:
            print(f"{datetime.datetime.now()}\nПроизошла ошибка {error}")
