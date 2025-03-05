import requests

# URL для запроса
url = "https://search.wb.ru/exactmatch/ru/common/v9/search"

# Параметры запроса
params = {
    "ab_testing": "false",
    "appType": "1",
    "curr": "rub",
    "dest": "-1257786",
    "lang": "ru",
    "query": "решето для муки",
    "resultset": "filters",
    "spp": "30",
    "suppressSpellcheck": "false",
}

# Заголовки запроса
headers = {
    "Host": "search.wb.ru",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Sec-Ch-Ua-Platform": "macOS",
    "Accept-Language": "en-GB,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="133", "Not(A:Brand";v="99"',
    "X-Captcha-Id": "Catalog 1|1|1742378662|AA==|d04b4770de2c4f08bbad62c69fa872a0|rYAKa5arKfrGJXvssSeDCWjYh0rcwwNJpsCSGKoCKeI",
    "Sec-Ch-Ua-Mobile": "?0",
    "X-Queryid": "qid148206511174109188520250305103149",
    "Accept": "*/*",
    "Origin": "https://www.wildberries.ru",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.wildberries.ru/catalog/0/search.aspx?search=%D1%80%D0%B5%D1%88%D0%B5%D1%82%D0%BE%20%D0%B4%D0%BB%D1%8F%20%D0%BC%D1%83%D0%BA%D0%B8",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i",
}

# Выполнение GET-запроса
response = requests.get(url, params=params, headers=headers)

# Проверка статуса ответа
if response.status_code == 200:
    print("Успешный запрос!")
    print(response.json())  # Вывод JSON-ответа
else:
    print(f"Ошибка запроса: {response.status_code}")
    print(response.text)
