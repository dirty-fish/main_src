import pandas as pd
import clickhouse_connect
import subprocess

def run_docker_clickHouse():
    command = [
        "sudo", "docker", "run", "-d", "--restart", "unless-stopped",
        "--name", "clickhouse_server",
        "-e", "CLICKHOUSE_DB=vz",
        "-e", "CLICKHOUSE_USER=default",
        "-e", "CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1",
        "-e", "CLICKHOUSE_PASSWORD=40951241",
        "-p", "9000:9000/tcp",
        "-p", "8123:8123/tcp",
        "clickhouse/clickhouse-server:latest"
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("ClickHouse запущен, ID контейнера:", result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print("Ошибка при запуске ClickHouse:", e.stderr)

def get_clickhouse_host():
    """
    Возвращает локальный хост и порт ClickHouse.
    """
    return "127.0.0.1", 8123  # Используем IP-адрес вместо localhost

def create_search_result_t(client):
    """
    Создаёт таблицу search_result в ClickHouse.
    """
    query = """
    CREATE TABLE IF NOT EXISTS search_result (
        time1 UInt32,
        time2 UInt32,
        wh UInt32,
        dtype UInt32,
        dist UInt32,
        id UInt64,
        root UInt64,
        kindId UInt32,
        brand LowCardinality(String),
        brandId UInt32,
        siteBrandId UInt32,
        subjectId UInt32,
        subjectParentId UInt32,
        name LowCardinality(String),
        entity String,
        matchId UInt64,
        supplier LowCardinality(String),
        supplierId UInt32,
        supplierRating Float32,
        supplierFlags UInt32,
        pics UInt32,
        reviewRating Float32,
        nmReviewRating Float32,
        feedbacks UInt32,
        nmFeedbacks UInt32,
        volume UInt32,
        viewFlags UInt64,
        price_total UInt32,
        totalQuantity UInt32,
        dt_add DateTime DEFAULT now(),
    )
    ENGINE = MergeTree()
    ORDER BY time1
    SETTINGS index_granularity = 8192;
    """
    try:
        client.command(query)
        print("✅ Таблица search_result успешно создана.")
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")

def create_search_big_t(client):
    """
    Create a table in ClickHouse for search queries.
    """
    table_name = "search_query_big"
    
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        `id_sq` Int32,
        `search_query` String,
        `frequency` Int64,
        `dt_add` DateTime
    ) ENGINE = MergeTree ORDER BY id_sq SETTINGS index_granularity = 8192;
    """
    
    try:
        client.command(query)
        print(f"✅ Таблица {table_name} успешно создана.")
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы {table_name}: {str(e)}")

def create_aggr_t(client, source_table, target_table):
    """
    Create a new table in ClickHouse based on the structure of an existing table.

    Args:
    - client (clickhouse_connect.Client): ClickHouse client object.
    - source_table (str): Name of the source table to copy structure from.
    - target_table (str): Name of the target table to create.

    Returns:
    - None
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {target_table} AS {source_table};
    """
    try:
        client.command(query)
        print(f"✅ Таблица {target_table} успешно создана на основе {source_table}.")
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы {target_table}: {str(e)}")

host, port = get_clickhouse_host()

def insert_csv_2click(client):
    # Загружаем CSV
    df = pd.read_csv("/Users/si/Documents/keys.csv")

    # Чистим названия столбцов от лишних пробелов
    df.columns = df.columns.str.strip()

    # Убедимся, что в CSV есть нужные колонки
    expected_columns = {"Unnamed: 0", "name", "frequency"}
    if not expected_columns.issubset(set(df.columns)):
        raise ValueError(f"CSV-файл должен содержать колонки {expected_columns}, но имеет {set(df.columns)}")

    # Переименовываем столбцы в соответствии с ClickHouse
    df = df.rename(columns={"Unnamed: 0": "id_sq", "name": "search_query"})

    # Убеждаемся, что столбцы имеют правильные типы
    df["id_sq"] = df["id_sq"].fillna(0).astype(int)
    df["search_query"] = df["search_query"].astype(str).fillna("")
    df["frequency"] = df["frequency"].fillna(0).astype(int)  # Убедимся, что частота целочисленная

    # Добавляем столбец `dt_add` с текущей датой и временем
    df["dt_add"] = pd.Timestamp.now()

    # Выводим первые строки, чтобы убедиться в структуре перед вставкой
    print("🔹 Данные перед вставкой:")
    print(df.head())

    # Оставляем только нужные столбцы
    df = df[["id_sq", "search_query", "frequency", "dt_add"]]

    # Преобразуем DataFrame в список кортежей
    data = list(df.itertuples(index=False, name=None))

    # Вставляем данные в ClickHouse
    client.insert("search_query_big", data, column_names=["id_sq", "search_query", "frequency", "dt_add"])

    print("✅ Данные успешно загружены в ClickHouse!")

run_docker_clickHouse
if host:
    print(f"🔍 Подключение к ClickHouse: {host}:{port}")
    client = clickhouse_connect.get_client(
        host=host,
        port=port,
        username="default",
        password="40951241",
        database="vz"
    )
    create_search_result_t(client)
    create_search_big_t(client)
    insert_csv_2click(client)
    create_aggr_t(client, "search_result", "search_result_agg")
else:
    print("❌ Не удалось найти контейнер ClickHouse.")
