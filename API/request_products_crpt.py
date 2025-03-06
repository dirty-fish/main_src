import requests

url = "https://search.wb.ru/exactmatch/ru/common/v9/search"
params = {
    "ab_testing": "false",
    "appType": "1",
    "curr": "rub",
    "dest": "-1257786",
    "lang": "ru",
    "page": "1",
    "query": "решето для муки",
    "resultset": "catalog",
    "sort": "popular",
    "spp": "30",
    "suppressSpellcheck": "false"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "*/*",
    "Origin": "https://www.wildberries.ru",
    "Referer": "https://www.wildberries.ru/catalog/0/search.aspx?search=решето%20для%20муки".encode("idna").decode("ascii")  # Исправленный заголовок Referer
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    print(response.json())  # Вывод JSON-ответа
else:
    print(f"Ошибка: {response.status_code}")