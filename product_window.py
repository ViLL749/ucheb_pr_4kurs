from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton, QLineEdit, QComboBox, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from db_manager import get_db_connection
from logger import log_product

class ProductCard(QFrame):
    def __init__(self, product_data, role):
        super().__init__()

        # Сохраняем  данные
        self.prod_id = product_data[0]
        self.prod_name_text = str(product_data[1])
        self.product_data = product_data



        self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            ProductCard {
                background-color: #FFFFFF;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-family: 'Times New Roman';
                font-size: 12pt;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 1. Левая часть (Фото)
        photo_block = QVBoxLayout()
        photo_label = QLabel()
        photo_label.setFixedSize(160, 160)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("border: 1px solid gray; background-color: #f9f9f9;")

        photo_filename = str(product_data[9]).strip()
        pixmap = QPixmap(f"photo/{photo_filename}")

        if pixmap.isNull():
            photo_label.setText("Фото отсутствует")
        else:
            photo_label.setPixmap(pixmap.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        photo_block.addWidget(photo_label)
        main_layout.addLayout(photo_block)

        # 2. Центр (Информация)
        center_widget = QWidget()
        center_widget.setStyleSheet("font-family: 'Times New Roman'; font-size: 13pt;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(4)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Сохраняем ссылку на QLabel имени для возможности выделения
        self.name_label = QLabel(f"<b>Наименование: {self.prod_name_text}</b>")
        center_layout.addWidget(self.name_label)

        center_layout.addWidget(QLabel(f"Категория: {product_data[2]}"))
        center_layout.addWidget(QLabel(f"Производитель: {product_data[3]}"))
        center_layout.addWidget(QLabel(f"Поставщик: {product_data[4]}"))
        center_layout.addWidget(QLabel(f"Цена: <font color='green'><b>{product_data[5]} р</b></font>"))
        center_layout.addWidget(QLabel(f"Гарантия: {product_data[10]} мес"))
        center_layout.addWidget(QLabel(f"Количество: {product_data[7]} шт"))

        main_layout.addWidget(center_widget, stretch=1)

        # 3. Правая часть (Скидка и Действия)
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)


        discount = product_data[6]
        discount_label = QLabel(f"Скидка:\n{discount}%")
        discount_label.setAlignment(Qt.AlignCenter)



        discount_label.setStyleSheet(f"""
            background-color: {'#2E8B57' if discount > 15 else '#7FFF00'};
            color: {'white' if discount > 15 else 'black'};
            font-family: 'Times New Roman';
            font-weight: bold;
            font-size: 13pt;
            padding: 10px;
            border-radius: 5px;
        """)

        discount_label.setFixedWidth(100)
        right_layout.addWidget(discount_label)

        # Кнопки для Администратора
        if role == "Администратор":
            right_layout.addSpacing(10)
            self.btn_edit = QPushButton("Редактировать")
            self.btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #00FA9A;
                    color: black;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #00e68a;
                }
            """)
            self.btn_delete = QPushButton("Удалить")
            self.btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #FF6347;
                    color: white;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #FF4500;
                }
            """)

            self.btn_edit.clicked.connect(self.edit_me)
            self.btn_delete.clicked.connect(self.delete_me)

            right_layout.addWidget(self.btn_edit)
            right_layout.addWidget(self.btn_delete)

        elif role == "Менеджер":
            right_layout.addSpacing(10)
            self.btn_order = QPushButton("В заказ")
            self.btn_order.setStyleSheet("""
                QPushButton {
                    background-color: #00FA9A;
                    color: black;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #00e68a;
                }
            """)
            right_layout.addWidget(self.btn_order)

        main_layout.addLayout(right_layout)

    def delete_me(self):

        msg = QMessageBox(self)
        msg.setWindowTitle("Удаление")
        msg.setText(f"Вы действительно хотите удалить товар:\n{self.prod_name_text}?")

        btn_yes = msg.addButton("Да", QMessageBox.AcceptRole)
        btn_no = msg.addButton("Нет", QMessageBox.RejectRole)

        msg.exec_()

        if msg.clickedButton() == btn_yes:
            try:
                conn = get_db_connection()
                cur = conn.cursor()

                cur.execute("DELETE FROM Products WHERE Article = ?", (self.prod_id,))

                log_product(
                    cur,
                    "Удаление",
                    self.prod_id,
                    self.prod_name_text,
                    self.window().user_name
                )

                conn.commit()
                conn.close()

                self.hide()

            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить товар: {e}")

    def edit_me(self):
        from product_form import ProductForm

        form = ProductForm(self.product_data)

        if form.exec_():

            conn = get_db_connection()
            cur = conn.cursor()

            log_product(
                cur,
                "Изменение",
                self.prod_id,
                self.prod_name_text,
                self.window().user_name
            )

            conn.commit()
            conn.close()

            window = self.window()
            if hasattr(window, "load_products"):
                window.load_products()



class ProductWindow(QWidget):
    def __init__(self, role, user_name="Гость"):
        super().__init__()
        self.role = role
        self.user_name = user_name
        self.found_cards = []
        self.current_match_index = -1
        self.setWindowTitle("Просмотр товаров")
        self.resize(1000, 700)  # Немного увеличим окно для удобства
        self.setWindowIcon(QIcon("resources/icon.png"))


        # Основной макет
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- ОБНОВЛЕННАЯ ШАПКА (ФИО справа) ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(15)

        logo = QLabel()
        pixmap = QPixmap("photo/logo.png")  # путь к твоему логотипу
        logo.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header_layout.insertWidget(0, logo)

        # 1. Слева: Фильтрация
        self.filter_combo = QComboBox()
        self.filter_combo.setFixedWidth(200)
        self.filter_combo.addItems(["Все производители", "ASUS", "Lenovo", "Apple", "HP", "Samsung"])
        self.filter_combo.currentTextChanged.connect(self.load_products)
        header_layout.addWidget(self.filter_combo)

        # 2. Слева: Поиск (если не Гость)
        if self.role in ["Менеджер", "Администратор"]:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по названию...")
            self.search_input.setMinimumWidth(250)  # Чтобы поле не было коротким
            self.search_input.textChanged.connect(self.highlight_search)
            header_layout.addWidget(self.search_input, stretch=2)

            # Кнопки навигации поиска рядом с полем
            nav_layout = QHBoxLayout()
            nav_layout.setSpacing(2)
            self.btn_prev = QPushButton("<")
            self.btn_next = QPushButton(">")
            self.btn_prev.setFixedSize(30, 25)
            self.btn_next.setFixedSize(30, 25)
            self.btn_prev.clicked.connect(lambda: self.navigate_search(-1))
            self.btn_next.clicked.connect(lambda: self.navigate_search(1))
            nav_layout.addWidget(self.btn_prev)
            nav_layout.addWidget(self.btn_next)
            header_layout.addLayout(nav_layout)

        # 3. ПРУЖИНА (Разделяет левую и правую части)
        header_layout.addStretch(1)

        # 4. Справа: Информация о пользователе
        # Выравниваем текст по правому краю
        user_info = QLabel(
            f"<div align='right'>Пользователь: <b>{self.user_name}</b><br>Роль: <i>{self.role}</i></div>")
        user_info.setStyleSheet("font-size: 12px; color: #333;")
        header_layout.addWidget(user_info)

        if self.role == "Администратор":
            btn_add = QPushButton("Добавить товар")

            btn_add.setStyleSheet("""
                QPushButton {
                    background-color: #00FA9A; 
                    color: black;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #00e68a;
                }
            """)

            btn_add.clicked.connect(self.add_product)

            header_layout.addWidget(btn_add)

        if self.role == "Администратор":
            btn_logs = QPushButton("Журнал операций")





            btn_logs.setStyleSheet("""
                QPushButton {
                    background-color: #7FFF00;
                    color: black;
                    font-family: 'Times New Roman';
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #66FF66;
                }
            """)

            btn_logs.clicked.connect(self.show_logs)

            header_layout.addWidget(btn_logs)



        # 5. Справа: Кнопка выхода
        btn_exit = QPushButton("Выйти")
        btn_exit.setFixedWidth(80)

        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;   
                color: black;
                font-family: 'Times New Roman';
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f2f2f2;
            }
        """)

        btn_exit.clicked.connect(self.logout)
        header_layout.addWidget(btn_exit)






        main_layout.addLayout(header_layout)

        # --- СКРОЛЛ (без изменений по логике, только имя) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_content = QWidget()
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(15)  # Расстояние между карточками

        self.load_products()

        self.scroll_area.setWidget(scroll_content)
        main_layout.addWidget(self.scroll_area)

    def load_products(self):
        # очистка карточек
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            manufacturer = self.filter_combo.currentText()

            query = """
                SELECT 
                p.Article,
                p.ProductName,
                c.CategoryName,
                m.ManufacturerName,
                s.SupplierName,
                p.Price,
                p.Discount,
                p.QuantityInStock,
                p.Description,
                p.Photo,
                p.WarrantyMonths
                FROM Products p
                LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
                LEFT JOIN Manufacturers m ON p.ManufacturerID = m.ManufacturerID
                LEFT JOIN Suppliers s ON p.SupplierID = s.SupplierID
            """

            params = []

            if manufacturer != "Все производители":
                query += " WHERE m.ManufacturerName = ?"
                params.append(manufacturer)

            cur.execute(query, params)
            products = cur.fetchall()

            conn.close()

            for prod in products:
                self.content_layout.addWidget(ProductCard(prod, self.role))

            if hasattr(self, 'search_input'):
                self.highlight_search()

        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def add_product(self):

        from product_form import ProductForm

        form = ProductForm()

        if form.exec_():
            conn = get_db_connection()
            cur = conn.cursor()

            log_product(
                cur,
                "Добавление",
                form.article.text(),
                form.name.text(),
                self.user_name
            )

            conn.commit()
            conn.close()

            self.load_products()

    def highlight_search(self):
        # Получаем текст из поиска и переводим в нижний регистр
        search_text = self.search_input.text().strip().lower()
        self.found_cards = []

        # Перебираем все карточки в макете
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if not item or not item.widget(): continue
            card = item.widget()

            # Сбрасываем стиль карточки к стандартному
            card.setStyleSheet("ProductCard { background: white; border: 1px solid gray; } * { outline: none; }")

            name = card.prod_name_text  # Берем оригинальное название товара

            if search_text and search_text in name.lower():
                # Логика выделения подстроки цветом
                start = name.lower().find(search_text)
                end = start + len(search_text)

                # Формируем HTML с оранжевым фоном для найденного куска текста
                highlighted_name = (
                    f"{name[:start]}"
                    f"<span style='background-color: #ff9d00; color: black;'>{name[start:end]}</span>"
                    f"{name[end:]}"
                )
                card.name_label.setText(f"<b>Наименование: {highlighted_name}</b>")

                # Подсвечиваем саму карточку желтым
                card.setStyleSheet(
                    "ProductCard { background: #ffffcc; border: 2px solid orange; } * { outline: none; }")
                self.found_cards.append(card)
            else:
                # Если совпадений нет, ставим обычный текст
                card.name_label.setText(f"<b>Наименование: {name}</b>")

        self.current_match_index = -1

    def navigate_search(self, step):
        if not self.found_cards: return

        # Сбрасываем интенсивную подсветку с предыдущей карточки
        if self.current_match_index != -1:
            prev_card = self.found_cards[self.current_match_index]
            prev_card.setStyleSheet(
                "ProductCard { background: #ffffcc; border: 2px solid orange; } * { outline: none; }")

        # Высчитываем индекс следующей карточки
        self.current_match_index += step
        if self.current_match_index >= len(self.found_cards): self.current_match_index = 0
        if self.current_match_index < 0: self.current_match_index = len(self.found_cards) - 1

        target_card = self.found_cards[self.current_match_index]

        # Выделяем текущую карточку красной рамкой
        target_card.setStyleSheet("ProductCard { background: #ffeb3b; border: 3px solid red; } * { outline: none; }")

        # Автоматически прокручиваем скролл к этой карточке
        self.scroll_area.ensureWidgetVisible(target_card)

    def show_logs(self):

        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem

        dialog = QDialog(self)
        dialog.setWindowTitle("Журнал операций")
        dialog.resize(900, 400)

        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setColumnCount(6)

        table.setHorizontalHeaderLabels([
            "Дата",
            "Пользователь",
            "Действие",
            "Артикул",
            "Товар",
            "Изменения"
        ])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT ActionTime, UserName, Action, ProductArticle, ProductName, Details
        FROM ProductLogs
        ORDER BY LogID DESC
        """)

        logs = cur.fetchall()
        conn.close()

        table.setRowCount(len(logs))

        for row_index, row in enumerate(logs):

            for col_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table.setItem(row_index, col_index, item)

        table.resizeColumnsToContents()

        layout.addWidget(table)

        dialog.exec_()

    def logout(self):
        from auth_window import AuthWindow

        self.auth_win = AuthWindow()
        self.auth_win.show()
        self.close()