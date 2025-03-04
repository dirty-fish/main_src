# Web Data Retrieval and Storage System

## English Version

### Overview
This Python-based system is designed for asynchronous web data retrieval and storage in a ClickHouse database. It efficiently processes search queries in parallel and stores product information.

### Main Components
- **assyncio**: Entry point that manages the asynchronous execution of data retrieval tasks.
- **read_web**: Core function that handles asynchronous product data retrieval from queues.
- **parse_insert**: Processes product data and inserts it into the ClickHouse database.
- **to_log**: Handles logging with timestamps and flexible output options.

### Features
- Asynchronous data processing
- Multiprocessing support for parallel task execution
- ClickHouse database integration
- Comprehensive logging system
- Queue-based task management

### Requirements
- Python with asyncio support
- ClickHouse database (running on `localhost:8123`)
- Access to required web services for data retrieval

### Database Configuration
The system connects to ClickHouse with the following default settings:
- **Host**: `localhost`
- **Port**: `8123`
- **Username**: `default`
- **Password**: `40951241`

### Logging
Logs are stored in:
- **Main log file**: `/home/ubuntu/LOGG.log`
- **SQL queries log**: `/home/ubuntu/SQLL`

Let me trace the data flow in the program by analyzing the key components and their connections.
Let me analyze the main data flow by checking some key functions:
Let me get more context about the worker function:
Let me check the calculate and assyncio functions:
Based on the analysis, here's the data flow in the program:
The program starts with RUN_QUERY which:
Sets up a multiprocessing environment with 30 worker processes
Connects to a ClickHouse database and truncates the vz.search_result table
Creates tasks for asynchronous processing
The data processing pipeline:
worker processes get tasks from a queue
Each worker executes calculate with the task parameters
The tasks are primarily calls to assyncio function
assyncio runs asynchronous operations through main
Key data structures:
task_queue: Holds tasks to be processed by workers
done_queue_sq: Tracks completed tasks
Database connection to ClickHouse for storing search results
The program appears to be designed for parallel processing of search queries, with results being stored in a ClickHouse database table named vz.search_result.
The system uses both multiprocessing (for parallel execution) and asyncio (for asynchronous I/O operations), making it efficient for handling multiple search operations simultaneously.

 I found that the query parameters are defined in the function map_query_params. The parameters passed to each query are:
ab_testing: False
appType: 1
curr: "rub" (currency)
dest: -1257786 (destination identifier)
query: The actual search key/term
resultset: "filters"
spp: 30 (search results per page)
suppressSpellcheck: False
These parameters are used when making requests to retrieve product data through the get_products function, which uses these parameters to construct the API request.

---

## Русская версия

### Обзор
Эта система на Python предназначена для асинхронного получения данных из веба и их хранения в базе данных ClickHouse. Она эффективно обрабатывает поисковые запросы в параллельном режиме и сохраняет информацию о продуктах.

### Основные компоненты
- **assyncio**: Точка входа, управляющая асинхронным выполнением задач по извлечению данных.
- **read_web**: Основная функция, выполняющая асинхронное извлечение данных о продуктах из очередей.
- **parse_insert**: Обрабатывает данные о продуктах и вставляет их в базу ClickHouse.
- **to_log**: Обеспечивает логирование с временными метками и гибкими настройками вывода.

### Особенности
- Асинхронная обработка данных
- Поддержка многопроцессорного выполнения задач
- Интеграция с базой данных ClickHouse
- Расширенная система логирования
- Управление задачами на основе очередей

### Требования
- Python с поддержкой asyncio
- База данных ClickHouse (работающая на `localhost:8123`)
- Доступ к необходимым веб-сервисам для получения данных

### Конфигурация базы данных
Система подключается к ClickHouse со следующими параметрами по умолчанию:
- **Хост**: `localhost`
- **Порт**: `8123`
- **Имя пользователя**: `default`
- **Пароль**: `40951241`

### Логирование
Логи хранятся в следующих файлах:
- **Основной лог-файл**: `/home/ubuntu/LOGG.log`
- **Лог SQL-запросов**: `/home/ubuntu/SQLL`

Позвольте мне проследить поток данных в программе, проанализировав ключевые компоненты и их связи.
Давайте проанализируем основной поток данных, проверив некоторые ключевые функции:
Давайте узнаем больше о функции worker:
Проверим функции calculate и assyncio:
На основании проведенного анализа вот поток данных в программе:
Программа начинается с RUN_QUERY, которая:
Устанавливает многопроцессорную среду с 30 рабочими процессами
Подключается к базе данных ClickHouse и усекает таблицу vz.search_result
Создает задачи для асинхронной обработки
Конвейер обработки данных:
рабочие процессы получают задания из очереди
Каждый рабочий процесс выполняет вычисления с параметрами задачи
Задачи - это прежде всего вызовы функций assyncio
assyncio выполняет асинхронные операции через main
Ключевые структуры данных:
task_queue: Хранит задачи, которые должны быть обработаны рабочими
done_queue_sq: отслеживает выполненные задания
Соединение базы данных с ClickHouse для хранения результатов поиска
Программа, судя по всему, предназначена для параллельной обработки поисковых запросов, а результаты хранятся в таблице базы данных ClickHouse с именем vz.search_result.
Система использует как мультипроцессинг (для параллельного выполнения), так и asyncio (для асинхронных операций ввода-вывода), что делает ее эффективной для одновременной обработки нескольких поисковых операций.

Я выяснил, что параметры запроса определены в функции map_query_params. Передаваемые параметры:
	•	ab_testing: False (отключение A/B-тестирования)
	•	appType: 1 (тип приложения)
	•	curr: "rub" (валюта — рубли)
	•	dest: -1257786 (идентификатор направления)
	•	query: (ключевое слово или поисковый запрос)
	•	resultset: "filters" (набор результатов)
	•	spp: 30 (количество результатов на странице)
	•	suppressSpellcheck: False (отключение проверки орфографии)

Эти параметры используются при запросах к API через функцию get_products, которая формирует запрос с их помощью для получения данных о товарах.
_____

