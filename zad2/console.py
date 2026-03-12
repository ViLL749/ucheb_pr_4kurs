import sqlite3
import csv
from datetime import datetime
from tabulate import tabulate
import os

DB_NAME = "../zad1/identifier.sqlite"


def log_query(query_name):
    with open("query_history.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {query_name}\n")


def save_to_csv(headers, rows, name):
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print("Файл сохранён:", filename)


def execute_query(query, name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    headers = [i[0] for i in cursor.description]

    print("\nРезультат:\n")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    log_query(name)

    save = input("\nСохранить в CSV? (y/n): ")
    if save.lower() == "y":
        save_to_csv(headers, rows, name)

    conn.close()


# 1 Топ 10 товаров
def top_products():
    query = """
    SELECT 
        p.ProductName as Название,
        p.Article as Артикул,
        c.CategoryName as Категория,
        SUM(oi.Quantity) AS Продано,
        SUM(oi.Quantity * p.Price) AS Выручка,
        COUNT(DISTINCT oi.OrderID) AS Заказов
    FROM OrderItems oi
    JOIN Products p ON oi.Article = p.Article
    LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
    GROUP BY p.ProductName, p.Article, c.CategoryName
    ORDER BY "Продано" DESC
    LIMIT 10;
    """
    execute_query(query, "top_products")


# 2 Выручка по месяцам
def revenue_by_month():
    query = """
    SELECT 
        strftime('%Y-%m', o.OrderDate) AS "Месяц",
        COUNT(DISTINCT o.OrderID) AS "Заказов",
        SUM(oi.Quantity * p.Price) AS "Выручка",
        ROUND(
            (SUM(oi.Quantity * p.Price) - 
                (SELECT IFNULL(SUM(oi2.Quantity * p2.Price), 0)
                 FROM Orders o2
                 JOIN OrderItems oi2 ON o2.OrderID = oi2.OrderID
                 JOIN Products p2 ON oi2.Article = p2.Article
                 WHERE strftime('%Y-%m', o2.OrderDate) < strftime('%Y-%m', o.OrderDate))
            ) * 100.0 /
            (SELECT IFNULL(SUM(oi2.Quantity * p2.Price), 0)
                 FROM Orders o2
                 JOIN OrderItems oi2 ON o2.OrderID = oi2.OrderID
                 JOIN Products p2 ON oi2.Article = p2.Article
                 WHERE strftime('%Y-%m', o2.OrderDate) < strftime('%Y-%m', o.OrderDate))
            , 2
        ) AS "Рост (%)",
        (
            SELECT IFNULL(SUM(oi2.Quantity * p2.Price), 0)
            FROM Orders o2
            JOIN OrderItems oi2 ON o2.OrderID = oi2.OrderID
            JOIN Products p2 ON oi2.Article = p2.Article
            WHERE strftime('%Y-%m', o2.OrderDate) <= strftime('%Y-%m', o.OrderDate)
        ) AS "Накоп. выручка"
    FROM Orders o
    JOIN OrderItems oi ON o.OrderID = oi.OrderID
    JOIN Products p ON oi.Article = p.Article
    GROUP BY strftime('%Y-%m', o.OrderDate)
    ORDER BY "Месяц";
    """
    execute_query(query, "revenue_by_month")


# 3 Товары без продаж
def products_without_sales():
    query = """
    SELECT
        p.Article AS "Артикул",
        p.ProductName AS "Товар",
        c.CategoryName AS "Категория",
        p.Price AS "Цена",
        p.QuantityInStock AS "Остаток"
    FROM Products p
    LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
    WHERE p.Article NOT IN (
        SELECT DISTINCT Article FROM OrderItems
    )
    ORDER BY p.ProductName;
    """
    execute_query(query, "products_without_sales")


# 4 Сегментация клиентов
def client_segmentation():
    query = """
    SELECT
        u.FIO AS "Клиент",
        COUNT(DISTINCT o.OrderID) AS "Заказов",
        SUM(oi.Quantity * p.Price) AS "Всего (Р)",
        ROUND(SUM(oi.Quantity * p.Price) * 1.0 / COUNT(DISTINCT o.OrderID), 2) AS "Ср. чек (Р)",
        CASE
            WHEN SUM(oi.Quantity * p.Price) < 10000 THEN 'Эконом'
            WHEN SUM(oi.Quantity * p.Price) BETWEEN 10000 AND 50000 THEN 'Стандарт'
            WHEN SUM(oi.Quantity * p.Price) BETWEEN 50000 AND 150000 THEN 'Премиум'
            ELSE 'VIP'
        END AS "Сегмент"
    FROM Users u
    JOIN Orders o ON u.UserID = o.UserID
    JOIN OrderItems oi ON o.OrderID = oi.OrderID
    JOIN Products p ON oi.Article = p.Article
    GROUP BY u.UserID, u.FIO
    ORDER BY "Всего (Р)" DESC;
    """
    execute_query(query, "client_segmentation")


# 5 Товары со скидкой выше средней по категории
def discount_above_average():
    query = """
    SELECT
        p.ProductName AS "Товар",
        c.CategoryName AS "Категория",
        p.Discount AS "Скидка (%)",
        ROUND(
            (SELECT AVG(p2.Discount)
             FROM Products p2
             WHERE p2.CategoryID = p.CategoryID), 2
        ) AS "Ср. по кат. (%)",
        ROUND(p.Discount - 
            (SELECT AVG(p2.Discount)
             FROM Products p2
             WHERE p2.CategoryID = p.CategoryID), 2
        ) AS "Разница (%)"
    FROM Products p
    JOIN Categories c ON p.CategoryID = c.CategoryID
    WHERE p.Discount >
        (SELECT AVG(p2.Discount)
         FROM Products p2
         WHERE p2.CategoryID = p.CategoryID)
    ORDER BY "Разница (%)" DESC;
    """
    execute_query(query, "discount_above_average")


# 6 Товары на грани исчерпания
def low_stock():
    query = """
        SELECT
        p.ProductName AS "Товар",
        p.Article AS "Артикул",
        c.CategoryName AS "Категория",
        p.QuantityInStock AS "Остаток",
        s.SupplierName AS "Поставщик",
        IFNULL((
            SELECT SUM(oi.Quantity)
            FROM OrderItems oi
            JOIN Orders o ON oi.OrderID = o.OrderID
            WHERE oi.Article = p.Article
              AND o.OrderDate >= date('now', '-30 day')
        ), 0) AS "Продано/30дн"
    FROM Products p
    LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
    LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID
    WHERE p.QuantityInStock < 5
    ORDER BY p.QuantityInStock ASC;
    """
    execute_query(query, "low_stock")


# 7 Постоянные клиенты
def loyal_clients():
    query = """
    SELECT
        u.FIO AS "Клиент",
        COUNT(DISTINCT o.OrderID) AS "Заказов",
        SUM(oi.Quantity) AS "Товаров",
        ROUND(100.0 * SUM(oi.Quantity) / (SELECT SUM(Quantity) FROM OrderItems), 2) AS "% Товаров",
        SUM(oi.Quantity * p.Price) AS "Сумма (Р)",
        ROUND(SUM(oi.Quantity * p.Price) * 1.0 / COUNT(DISTINCT o.OrderID), 2) AS "Ср. стоимость (Р)"
    FROM Users u
    JOIN Orders o ON u.UserID = o.UserID
    JOIN OrderItems oi ON o.OrderID = oi.OrderID
    JOIN Products p ON oi.Article = p.Article
    GROUP BY u.UserID, u.FIO
    HAVING COUNT(DISTINCT o.OrderID) > 3
    ORDER BY "Сумма (Р)" DESC;
    """
    execute_query(query, "loyal_clients")


# 8 Статистика заказов по статусам
def order_status_stats():
    query = """
    SELECT
        s.StatusName AS "Статус",
        COUNT(DISTINCT o.OrderID) AS "Заказов",
        ROUND(100.0 * COUNT(DISTINCT o.OrderID) / (SELECT COUNT(*) FROM Orders), 2) AS "% Заказов",
        SUM(oi.Quantity * p.Price) AS "Сумма (Р)",
        ROUND(SUM(oi.Quantity * p.Price) * 1.0 / COUNT(DISTINCT o.OrderID), 2) AS "Ср. стоимость (Р)"
    FROM Orders o
    JOIN Statuses s ON o.StatusID = s.StatusID
    JOIN OrderItems oi ON o.OrderID = oi.OrderID
    JOIN Products p ON oi.Article = p.Article
    GROUP BY s.StatusID, s.StatusName
    ORDER BY "Заказов" DESC;
    """
    execute_query(query, "order_status_stats")


def menu():
    while True:
        print("\n====== АНАЛИТИКА МАГАЗИНА ======")
        print("1. Топ 10 продаваемых товаров")
        print("2. Выручка по месяцам")
        print("3. Товары без продаж")
        print("4. Сегментация клиентов")
        print("5. Товары со скидкой выше средней")
        print("6. Товары на грани исчерпания")
        print("7. Постоянные клиенты")
        print("8. Статистика заказов")
        print("0. Выход")

        choice = input("Выберите пункт: ")

        if choice == "1":
            top_products()
        elif choice == "2":
            revenue_by_month()
        elif choice == "3":
            products_without_sales()
        elif choice == "4":
            client_segmentation()
        elif choice == "5":
            discount_above_average()
        elif choice == "6":
            low_stock()
        elif choice == "7":
            loyal_clients()
        elif choice == "8":
            order_status_stats()
        elif choice == "0":
            print("Выход...")
            break
        else:
            print("Неверный выбор")



menu()