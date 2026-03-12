# Учебная практика за 8 семестр #

#### Ход работы ####

##### Задание №1.

> Создайте следующие запросы:
1.  Топ 10 товаров по продажам
    * Команда
        ```sql 
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
        ```
    * Результат

        ![prim1.png](readme_source/prim1.png)

2.  Выручка по месяцам
    * Команда
        ```sql
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

        ```
    * Результат

        ![prim2.png](readme_source/prim2.png)

3.  Товары без продаж
    * Команда
        ```sql 
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
        ```
    * Результат

        ![prim3.png](readme_source/prim3.png)



4.  Сегментация клиентов
    * Команда
        ```sql 
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

        ```
    * Результат

        ![prim4.png](readme_source/prim4.png)

5.  Товары со скидкой выше средней по категории
    * Команда
        ```sql
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
        ```
    * Результат

        ![prim5.png](readme_source/prim5.png)

6.  Товары на грани исчерпания
    * Команда
        ```sql 
        DELIMITER //
        CREATE PROCEDURE classes_by_period(IN start_date DATE, IN end_date DATE)
        BEGIN
            SELECT
                c.id        AS `ID занятия`,
                sub.name    AS `Предмет`,
                t.name      AS `Преподаватель`,
                c.d_class   AS `Дата занятия`
            FROM classes c
            JOIN subjects sub ON c.subject = sub.id
            JOIN teachers t ON c.teacher = t.id
            WHERE c.d_class BETWEEN start_date AND end_date
            ORDER BY c.d_class;
        END //
        DELIMITER ;
        ```
    * Результат

        | ID занятия | Предмет | Преподаватель | Дата занятия |
        | :--- | :--- | :--- | :--- |
        | 5 | ТРПО | Кацина А. С. | 2020-10-11 |
        | 23 | ТРПО | Кацина А. С. | 2020-11-02 |


7.  Постоянные клиенты
    * Команда
        ```sql 
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
        ```
    * Результат

        ![prim7.png](readme_source/prim7.png)


8.  Статистика заказов по статусам
    * Команда
        ```sql 
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
        ```
    * Результат

        ![prim8.png](readme_source/prim8.png)

