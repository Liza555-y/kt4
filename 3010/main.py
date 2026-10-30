import pandas as pd
import redis

# 1. Загружаем данные с GitHub
url = "https://raw.githubusercontent.com/junaart/ForStudents/main/Big_Data/data_%D0%A3%D0%9A.xlsx"

data = pd.read_excel(url)

print("Всего строк в исходном файле:", len(data))


# 2. Выбираем необходимые столбцы
org = "Наименование управляющей организации, жилищного объединения"
orders = "Выдано предписаний"
fines = "Сумма штрафа (тыс. руб.)"


# 3. Отбираем организации с количеством предписаний > 10
data[orders] = pd.to_numeric(data[orders], errors="coerce")

result = data[data[orders] > 10]

result = result[[org, orders, fines]]

print("\nКоличество отобранных записей:", len(result))
print("\nПервые 10 записей:")
print(result.head(10).to_string(index=False))


# 4. Подключаемся к Redis
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

print("\nПодключение к Redis:", r.ping())


# 5. Удаляем старые результаты этого задания
for key in r.scan_iter("organization:*"):
    r.delete(key)


# 6. Сохраняем организации в виде хэш-таблиц
with r.pipeline() as pipe:
    for i, (name, count, fine) in enumerate(
        result.itertuples(index=False, name=None), start=1
    ):
        pipe.hset(
            f"organization:{i}",
            mapping={
                "Организация": str(name),
                "Выдано предписаний": str(int(count)),
                "Сумма штрафов, тыс. руб.": str(fine)
            }
        )

    pipe.execute()


print("\nСохранено записей в Redis:", len(result))


# 7. Проверяем сохранённые данные
print("\nПример хэш-таблицы:")
print(r.hgetall("organization:1"))

print("\nКоличество хэш-таблиц:",
      sum(1 for _ in r.scan_iter("organization:*")))