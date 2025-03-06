import sys
sys.path.append("/home/ubuntu/.local/lib/python3.8/site-packages/")
##import os
##import requests
##from requests import get  #from requests import json
import clickhouse_connect   # HttpClient

import datetime
from datetime import datetime

import asyncio
import time
import aiohttp
#import wildberries
#from wildberries import get_products #, get_products_detail

import orjson
import multiprocessing

import shutil

#### ПАРАЛЛЕЛЬНОЕ ВЫПОЛНЕНИЕ ПОЛУЧЕНИЯ WEB-ДАННЫХ И ЗАНЕСЕНИЕ ДАННЫХ В БАЗУ ДАННЫХ
#### очередь поисковых запросов --> WEB-данные --> Парсинг --> Запись в Clickhouse

SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"

regions = ",".join(map(str, [80, 64, 38, 4, 115, 83, 33, 68, 70, 69, 30, 86, 75, 40, 1, 66, 48, 110, 31, 22, 71, 114]))

dir_log='/home/ubuntu/'

########################
## Функция 1 для организации многопроцессности
## Пытался объединить Функция 1  и Функция 2 - не вышло!
def worker(input,output):
    """Функция, выполняемая рабочими процессами"""
    for func, args in iter(input.get, 'STOP'):
        result = calculate(func, args)

## Функция 2 для организации многопроцессности
def calculate(func, args):
    """Функция, используемая для вычисления результата"""
    proc_name = multiprocessing.current_process().name
    result = func(*args) ## выполнение функции из очереди заданий task_queue
    return f'{proc_name}, результат функции {func.__name__}{args} = {result}'

#########################################

def free_disc(disc): #имя диска
#disc="C:"
    ttt=[]
    for k in shutil.disk_usage(disc):
        ttt.append(k) ## 0 - всего.    1 - занято.  2 - свободно
    nnn=round((ttt[2]/ttt[0])*100,1)
    to_log('Свободно '+str(nnn)+'% диска '+disc+', это '\
          +str(round(ttt[2]/(1024*1024*1024),1))+' гигабайт.',1)
    return nnn

def to_log(str, eprint=0): #Логирование в файл
            #eprint=0 - печать на экран не идет, 1- идет, 5 - создается новый файл лога
    ff=dir_log+'LOGG.log'
    noww=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if eprint==5: ## создание нового файла лога
        with open(ff, 'w+') as f: # Заносим лог в файл
            f.write(noww+' # Создан этот лог в файле '+ff+'\n')
            f.write(noww+' # '+str+'\n')
        print(noww+': Создан файл лога - '+ff)
    else:
        if eprint==1:
            print(noww+' # '+str)
        with open(ff, 'a') as f: # Добавляем лог в файл
            f.write(noww+' # '+str+'\n')

#########################

# Функция для маппинга данных
def map_product_data(product_data):
    # Маппинг полей продукта из JSON
    return {
        "id": product_data.get("id"),
        "name": product_data.get("name"),
        "brand": product_data.get("brand"),
        "brandId": product_data.get("brandId"),
        "rating": product_data.get("rating"),
        "feedbacks": product_data.get("feedbacks"),
        "price": product_data["sizes"][0]["price"]["product"] if product_data.get("sizes") else None,
        "sizes": [size.get("name") for size in product_data.get("sizes", [])],
        "colors": [color.get("name") for color in product_data.get("colors", [])],
        "subjectId": product_data.get("subjectId"),
        "supplier": product_data.get("supplier"),
        "supplierRating": product_data.get("supplierRating"),
        "pics": product_data.get("pics"),
    }

# Функция для маппинга тела запроса


# Функция для маппинга query-параметров
def map_query_params(key: str):
    return {
        "ab_testing": False,
        "appType": 1,
        "curr": "rub",
        "dest": -1257786,
        "query": key,
        "resultset": "filters",
        "spp": 30,
        "suppressSpellcheck": False
    }

# Функция для получения продуктов с маппингом
async def get_products(key: str, client_session, used: bool = False):
    # Маппинг query-параметров
    query_params = map_query_params(key)

    async with client_session.get(SEARCH_URL, params=query_params) as raw_data:
        try:
            response_data = await raw_data.json(content_type="text/plain")
            # Маппим только поле data["products"]
            products = [map_product_data(product) for product in response_data["data"]["products"]]
            return key, products
        except Exception as error:
            if not used:
                return await get_products(key, client_session, True)

def parse_insert(products,spisok_zaprosov):
    ## парсинг полученных web данных в INSERT а потом запись в Клик


    list_id_search=spisok_zaprosov[1] ## тут список id_search

    time_parse21 = time.time()
    nf=0 ## порядковый номер поискового запроса в группе из 100 запросов
    big_insert=['INSERT INTO vz.search_result values '] # создаем список для большого INSERTа - 10 000 записей
    first_record=1 ## Признак первой записи - ставить запятую или нет
    ##tv=datetime.now().strftime("%Y-%m-%d %H:%M:%S")       # ТЕКУЩЕЕ ВРЕМЯ в строковом формате

    for tuplee in products: # tuplee - данные отдельного поискового запроса
                            #(100 товаров) в виде кортежа
        s=orjson.dumps(tuplee, option=orjson.OPT_INDENT_2).decode()

        ## тут стандартизовнный поисковый запрос!
        standart_s_query=s[s.find('"')+1:s.find('",')]

        ## Экранируем кавычку!
        standart_s_query="'"+standart_s_query.replace("'", "''")+"'"
        #print(standart_s_query)


        ## тут поисковый запрос правильнее чем в исходном поисковом запросе!!!

        ##if spisok_zaprosov[0][nf]!=standart_s_query:
            ##to_log(spisok_zaprosov[0][nf-1]+' *** '+spisok_zaprosov[0][nf]+' *** '+standart_s_query+ ' *** '+ str(nf)) ##


        ## Пока не используем, тк процессы конфликтуют за этот файл - нужны разные имена!
        ##if nf==0:#ТЕСТОВАЯ ЗАПИСЬ JSON   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ##    with open(dir_log+'JSON.txt', 'w') as f: # Заносим JSON в файл
        ##        f.write(s)

        ##id_search=list_id_search[nf] ## ID поискового запроса
        id_search='0' ## не используется!

        insert_txt=''

        l_max=0
        pos=2 #текущая позиция
        kk=1
        pp=0 # Позиция товара в выдаче из 100 товаров
        while True: # Цикл разбора полученной страницы
                  # ОСНОВНЫЕ ПОЛЯ
            nnn=s.find('"time1":', pos)   # Начало строки товара
            if nnn==-1: # Товары кончились!
                #print('бдям 1 = ', pos)
                #print('вау 1 = ', s[:3000])
                    break
            kkk=s.find('"time1":', nnn+6)   # Начало строки следующего товара
            if kkk==-1: #Последний товар в выдаче страницы
                stro=s[nnn-1:]
                pos=nnn+6
                #print('бдям 2 = ', nnn)
            else:
                pos=kkk-1  # Позиция следующего товара
                #print(pos)
                stro=s[nnn-1:kkk-1] # Вырезали строку с тегами товара
            if len(stro)>80000:
                #print('Длинный JSON =',stro[:3000])
                to_log('Длинный JSON ='+stro[:3000], 1)
                break

            #print(stro)

            # Получим строку с содержимым списка тегов
            line=get_content_tags\
                  (stro,["time1","time2","dist","id","root","kindId","subjectId",\
                         "subjectParentId","name","brand","brandId","siteBrandId",\
                         "supplier","supplierId","sale","priceU","salePriceU",\
                         "logisticsCost","saleConditions","returnCost","pics",\
                         "rating","reviewRating","feedbacks","volume","viewFlags"])

# [{"time1":6,"time2":29,"dist":155,"id":172602259,"root":118908611,"kindId":2,"subjectId":2605,"subjectParentId":5038,
#"name":"Стразы с доступом эротические","brand":"ZLATON","brandId":310434805,"siteBrandId":0,"supplier":"ZLATON",
#"supplierId":1163649,"sale":31,"priceU":55000,"salePriceU":37500,"logisticsCost":0,"saleConditions":0,
#"returnCost":0,"pics":11,"rating":5,"reviewRating":4.8,"feedbacks":389,"isAdult":true,"volume":4,"viewFlags":0,

            # Цвет и размер!!!

            nnn1=s.find('"time1":',pos) # позиция след товара - у последнего нет этого
            nnn2=s.find('"colors":',pos) # позиция "colors"

            if nnn1==-1:
                colors=s[nnn2:]
            else:
                colors=s[nnn2:nnn1-1]

            colors='colors'  ## временно тк дает ошибку 2023-11-29

            colors="'"+colors+"'"

            insertt='('+line+','+colors+ ','+ id_search +",'"+tv+"',"\
                     +str(pp)+","+standart_s_query+")"

            if l_max<len(insertt):
                l_max=len(insertt)
            if len(insertt)>80000:
                #print('JSON =',stro[:3000])
                #print('line =',line)
                #print('colors =',colors)
                #print('Длинная строка =',insertt[:2000])
                to_log('JSON = '+stro[:3000], 1)
                to_log('line = '+line, 1)
                to_log('colors ='+colors, 1)
                to_log('Длинная строка = '+insertt[:2000], 1)
                break

            if first_record==1: ## Первая запись - запятую не ставим
                first_record=0
                big_insert.append(insertt)
            else: ## НЕ Первая запись - запятую ставим
                big_insert.append(', '+insertt)

            pp=pp+1
            if pp>120:
                to_log('Зациклились! \n\n\n'+s[:3000], 1)
                #print('Зациклились!')
                #print()
                #print(s[:3000])
                break
# Цикл разбора полученной страницы - конец

        ccc=pp ## Количество записанных товаров


                ## ccc - количество найденных товаров

        nf=nf+1 ## порядковый номер поискового запроса в группе из 100 запросов
# Цикл разбора пакета страниц - конец

    bi_str=''.join(big_insert)

    time_parse3 = time.time()

            #ТЕСТОВАЯ ЗАПИСЬ ЗАПРОСА   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ##with open(os.getcwd()+'/SQL_1.txt', 'w') as f: # Заносим SQL в файл
          ##  f.write(bi_str)
    ggg=insert_click(bi_str) ## Запись в clickhouse

    time_parse41 = time.time()
    return round(time_parse41-time_parse21,3)

##async
def insert_click(bi_str): # Выполнение полученного INSERTa в clickhouse
    time_parse4 = time.time()

    ## отладочная запись

    with open(dir_log+'SQLL', "w") as file: # пишем в файл SQL для 100 запросов
        file.write(bi_str)

    clickhouse_client = clickhouse_connect.create_client(host="localhost", username="default", port=8123,password = '40951241',database = 'vz')

    result=clickhouse_client.command(bi_str)  # Многострочная запись в таблицу vz.search_result

    time_parse5 = time.time()

    ##print('Время записи в БД =',round(time_parse5-time_parse4,3),' сек')

    ##print(result)


    #print('Время парсинга =',round(time_parse3-time_parse2,3),' сек')
    #print('Время записи в файлы =',round(time_parse4-time_parse3,3),' сек')


    ##print('RRRRRRRRRRRRRRRRR')
    return 1
##################################################

def get_content_tag(stroka,tag): # получить содержание тега по его названию
# stroka - строка в которой находится тег, tag - имя тега. Если тег не найден - возвращается пустое значение
    if tag=='name':
        n=stroka.find('"name":',stroka.find('"subjectParentId":')+10)
    else:
        n=stroka.find('"'+tag+'":')

    if n==-1:
        return ''
    lll=len(tag)+n+4 # позиция начала содержимого тега   было lll=len(tag)+n+3
                     # тк не было разделяющего пробела
    if stroka[lll]=='"': # в тэге - символьная строка
        ###mmm=stroka.find(', "',lll+1)  # начало следующего тэга
        n2=stroka.find('":',lll+1) ## разделитель следующего тэга
        mmm = stroka[lll:n2].rfind(',')-1 ## длина содержимого нужного тэга
        ##mmm=stroka.find('",',lll+1)  # конец этого тэга
        if mmm==-1:
            to_log('Не найдена концевая запятая в тэге = '+tag+', в строке: '+\
                   stroka[lll-15:lll+50],1)
            return "''"
        else:
            if mmm>100:
                to_log('Удивительно 555: mmm = '+str(mmm)+'.'+stroka[lll:lll+mmm+1],1)

            #kkk="'"+stroka[lll+1:lll+mmm].replace("'", "''")+"'"
            #print('stroka =',stroka)
            #print('tag =',tag,', содержимое =',kkk,', lll и mmm =', lll, mmm)

            return "'"+stroka[lll+1:lll+mmm].replace("'", "''")+"'" # Экранируем одинарную кавычку
    return stroka[lll:stroka.find(',',n)]



def get_content_tags(stroka,tags): # получить содержание списка тегов по их названию (через запятую - для формировния INSERT)
# stroka - строка в которой находится тег, tags - список тегов. Если тег не найден - возвращается пустое значение
    stroka_value=''
    for i in tags:
        stroka_value=stroka_value+get_content_tag(stroka,i)+','
    return stroka_value[:-1]


# ПРОГРАММА выборки поисковых запросов из БД Click и выдачи их в очередь done_queue_sq

def select_search_query(mask):
    clickhouse_client = clickhouse_connect.create_client(host="localhost", username="default", port=8123,password = '40951241',database = 'vz')
    to_log('ПОИСКОВЫЙ ЗАПРОС = '+mask, 1)

    ##tv=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    td1=datetime.utcnow()

    ##limit 2000    коляска
    #select id_sq from vz.search_query where search_query like '%шапка%' FORMAT Vertical

    ## mmm - выборка из таблицы vz.search_query_big по маске
    mmm=clickhouse_client.command(\
        "select * from vz.search_query_big where search_query like '"+\
        mask+"' FORMAT CSV")

    #print('********************')
    #print(mmm)
    #ll=type(mmm)
    #print(isinstance(mmm, str))
    #print('********************')

    if isinstance(mmm, str)==False:
        to_log('Поисковых запросов не найдено!',1)
        return 0

    list_query=mmm.split('\n') ## Заносим запросы в список

    nzap=100
    ##nzap=500 # Число параллельных асинхронных сессий для доступа в WEB

    page_limit=2 # Количество страниц выдачи на каждый поисковый запрос - пока не используется

    spisok_zapros=[] # Пустой список запросов - набираем 100 штук
    spisok_id=[] # Пустой список ID - набираем 100 штук

    stz=0  # Счетчик запросов в списке запросов

    nnn=0 # Число найденных запросов

    for zapis in list_query:

        nnn=nnn+1

        polia=zapis.split(',"')
        ## в записи три поля: ID запроса, Запрос, время записи запроса в таблицу vz.search_query_big
        spisok_zapros.append(polia[1][:-1]) # Добавляем сам запрос в список запросов
        spisok_id.append(polia[0]) # Добавляем ID запроса в список ID запросов

        stz=stz+1

        if (stz>=nzap): # Набрали нужное число запросов или запросы кончились - выполняем запросы к сайту
        ##!!print()
        ##!!print('Еще группа ',stz,' запросов:')
        ##!!print()
        ##!!print(spisok_zaprosov)

            ## Группу поисковых запросов - в очередь done_queue_sq
            spisok_zaprosov=[spisok_zapros] ##
            spisok_zaprosov.append(spisok_id) ##

            ## передача запросов через очередь в read_web
            done_queue_sq.put(spisok_zaprosov)

            spisok_zapros=[] # Пустой список запросов - набираем 100 штук
            spisok_id=[]
            stz=0  # Счетчик запросов в списке запросов

    ## Цикл кончился - выдаем в очередь оставшиеся запросы

    spisok_zaprosov=[spisok_zapros] ##
    spisok_zaprosov.append(spisok_id) ##
    done_queue_sq.put(spisok_zaprosov)

    ## ПРОЦЕССЫ ЗАКРЫВАЮТСЯ В МОДУЛЕ read_web!
    proc_name = multiprocessing.current_process().name
    #print('Процесс =',proc_name,'; Время работы Select_Search_Query ='\
     #     ,round((datetime.utcnow()-td1).total_seconds(),3), 'секунд')
    to_log('Процесс = '+proc_name+'; Время работы Select_Search_Query ='+\
           str(round((datetime.utcnow()-td1).total_seconds(),3))+\
           ' секунд. Найдено запросов '+str(nnn), 1)
    return 1

async def read_web():
    #### ПОЛУЧЕНИЕ Группы поисковых запросов из очереди done_queue_sq
    time_parse11 = time.time()

    paket=0 ## число обработанных пакетов

    proc_name = multiprocessing.current_process().name ## Название процесса

    lll=proc_name.find('-')

    if lll>-1:
        delay=int(proc_name[lll+1:])
    else:
        delay=0

    await asyncio.sleep(delay*0.01) ## Чтобы одновременно не бросались на пустую очередь
    ## и не было ошибки пустой очереди

    while True:
        size = done_queue_sq.qsize()

        if size==0:
            break

        spisok_zaprosov=done_queue_sq.get(timeout=20) ##

        #spisok_zaprosov[0] - список поисковых запросов
        #spisok_zaprosov[1] - список ID поисковых запросов

        paket=paket+1

        time_parse1 = time.time()

        async with aiohttp.ClientSession() as session:
            products = [data for data in await asyncio.gather(
                *[get_products(key, session) for key in spisok_zaprosov[0]]) if data]

        time_parse21 = time.time()

        ## Передаем выдачу + список ID запросов
        mmm=parse_insert(products,spisok_zaprosov) ## mmm - время работы

        # ПОКА УБРАЛ ТЕСТОВУЮ ПЕЧАТЬ
        ##to_log('Получение из интернета = '+
        ##      str(round(time_parse21-time_parse1,3)) + \
        ##      ' сек; Парсинг и вставка = '+str(mmm), 1)



    ## WHILE завершен
    time_parse22 = time.time()

    to_log('Процесс = '+proc_name+';  ПОЛНОЕ ВРЕМЯ РАБОТЫ read_web ='+\
          str(round(time_parse22-time_parse11,3))+\
          ' сек; Обработанных пакетов = ' + str(paket), 1)

    to_log('STOP.', 1)

    return 1

async def main():
    t1 = time.time()
    task1 = asyncio.create_task(read_web())
    await task1
    t2 = time.time()
    #Добавляем в лог
    to_log('ПОЛНОЕ ВРЕМЯ РАБОТЫ main = '+str(round(t2-t1,3))+' сек;', 1)
    return 1

def assyncio(p,t):
    asyncio.run(main())
    return 5


def RUN_QUERY(mask): # Маска, по которой отбираются поисковые запросы, %% - без маски
## ОСНОВНАЯ ПРОГРАММА - ЗАПУСК нескольких ПАРАЛЛЕЛЬНЫХ ЗАДАЧ read_web()
## Теперь работаем только с очередями, скрипт автоматом назначает для функции свободный процесс

    # Запуск 28 параллельных рабочих процессов под именем
    # параметры - входная очередь заданий и выходная очередь результатов
    NUMBER_OF_PROCESSES = 30

    for i in range(NUMBER_OF_PROCESSES):
        multiprocessing.Process(target=worker, args=(task_queue,done_queue_sq)).start()

   ## Чистим таблицу vz.search_result
    clickhouse_client = clickhouse_connect.create_client(host="localhost",username="default", port=8123,password = '40951241',database = 'vz')
    SQLL='TRUNCATE TABLE IF EXISTS vz.search_result'
    result=clickhouse_client.command(SQLL)  # Чистим таблицу vz.search_result


    i=select_search_query(mask) ## Заполнение очереди поисковых запросов done_queue_sq

    ## Готовим список параллельных задач
    TASKS1 = [(assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7)),(assyncio, (9, 7)),(assyncio, (9, 7)),\
              (assyncio, (9, 7))]

    for task in TASKS1:
        task_queue.put(task)  ## Запустили 28 штук read_web

    while True: # ждем когда очередь опустеет
        size = done_queue_sq.qsize()
        if size==0:
            break
        else:
            time.sleep(1)

    for i in range(NUMBER_OF_PROCESSES):  ## Завершаем все процессы!
        task_queue.put('STOP')
    return 1

def copy_to_agg(): #Перегон товаров из vz.search_result в vz.search_result_agg
# с агрегацией по ID товара и склейкой поисковых запросов,
#по которым этот товар был получен

    to_log('Начали перегон товаров из vz.search_result в vz.search_result_agg',1)

    clickhouse_client = clickhouse_connect.create_client(host="localhost",username="default", port=8123,password = '40951241',database = 'vz')
    SQLL='INSERT into vz.search_result_agg SELECT '+\
      ' max(time1) as time1,'+' max(time2) as time2,'+\
      ' max(dist) as dist,'+'id,'+' max(root) as root,'+\
      ' max(kindId) as kindId,'+' max(subjectId) as subjectId,'+\
      ' max(subjectParentId) as subjectParentId,'+' max(name) as name,'+\
      ' max(brand) as brand,'+' max(brandId) as brandId,'+\
      ' max(siteBrandId) as siteBrandId,'+' max(supplier) as supplier,'+\
      ' max(supplierId) as supplierId,'+' max(sale) as sale,'+\
      ' max(priceU) as priceU,'+' max(salePriceU) as salePriceU,'+\
      ' max(logisticsCost) as logisticsCost,'+\
      ' max(saleConditions) as saleConditions,'+' max(returnCost) as returnCost,'+\
      ' max(pics) as pics,'+' max(rating) as rating,'+\
      ' max(reviewRating) as reviewRating,'+' max(feedbacks) as feedbacks,'+\
      ' max(volume) as volume,'+' max(viewFlags) as viewFlags,'+\
      ' max(json_color_size) as json_color_size,'+' 0 as id_search,'+\
      ' max(dt_add) as dt_add,'+' 0 as product_rating,'+\
      "groupArray(concat(search_query, ':',substr(concat('0', toString(product_rating)),-2,2))) as search_query"+\
      ' FROM vz.search_result Group by id' # limit 100 FORMAT Vertical'

    #print(SQLL)

    result=clickhouse_client.command(SQLL)  # запись в таблицу vz.search_result_agg

    ## Убрал оптимизацию, тк дает ошибку таймаута
    ##to_log('Начали оптимизацию таблицы vz.search_result_agg',1)

    ##SQLL='OPTIMIZE TABLE vz.search_result_agg FINAL DEDUPLICATE'

    ##SQLL='OPTIMIZE TABLE vz.search_result_agg FINAL'

    ##result=clickhouse_client.command(SQLL)

    to_log('Завершили перегон товаров из vz.search_result в vz.search_result_agg',1)

    return 1


## СТАРТ ## СТАРТ ## СТАРТ ## СТАРТ ## СТАРТ ## СТАРТ ## СТАРТ ## СТАРТ

#print('Раз!')

to_log('', 5) #Создаем лог в файле

#print('Два!')

to_log('Поехали!', 1) #Начали лог

#print('Три!')

if free_disc("/")<10: #имя диска  - если на диске свободно < 10% места - то выходим
    to_log('На диске мало места, уходим.', 1) #Создаем лог в файле

# Создание очередей заданий и результатов
task_queue = multiprocessing.Queue()   ## входная очередь заданий

## выходная очередь результатов работы функции получения из БД поисковых запросов
done_queue_sq = multiprocessing.Queue()


kkk=round(time.time()) ## Время старта

for i in range (24): ## Суточный прогон range (24)
    while round(time.time())<kkk+i*3600:
        time.sleep(300)
        to_log('Ждемс ...', 1) #лог

    # Глобальная переменная ТЕКУЩЕЕ ВРЕМЯ - Для записи в таблицу результата
    tv=datetime.now().strftime("%Y-%m-%d %H:%M:%S") # ТЕКУЩЕЕ ВРЕМЯ в строковом формате

    to_log('Прогон № '+str(i)+ ' начался', 1) #лог
    RUN_QUERY('%%') ## %фл%; %вагнер%; флаг вагнер; вагнер флаг; запрещены!
                            ##%девочек%   шапка

    time.sleep(60) ## Ждем 1 минуту чтобы все запросы отработали
    to_log('Прогон № '+str(i)+ ' завершен', 1) #лог
    time.sleep(120) ## Ждем еще 2 минуты чтобы совсем все запросы отработали
    copy_to_agg()   #Перегон товаров из vz.search_result в vz.search_result_agg

to_log('Прогон полностью завершен', 1) #лог

#RUN_QUERY('%обувь%')
#to_log('ПЕРЕХОДИМ К СЛЕД ЗАПРОСУ',1) #Создаем лог в файле
#RUN_QUERY('%колготки%')
#to_log('ПЕРЕХОДИМ К СЛЕД ЗАПРОСУ',1) #Создаем лог в файле
#RUN_QUERY('%шуба%')






