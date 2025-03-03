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

