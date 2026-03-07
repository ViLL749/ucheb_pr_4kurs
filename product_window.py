from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton, QLineEdit, QComboBox, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from db_manager import get_db_connection


class ProductCard(QFrame):
    def __init__(self, product_data, role):
        super().__init__()

        # Сохраняем важные данные
        self.prod_id = product_data[0]
        self.prod_name_text = str(product_data[1])  # Для логики поиска

        # Настройка внешнего вида и УДАЛЕНИЕ БАГА С ОБВОДКОЙ (focus outline)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            ProductCard {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
            }
            * {
                outline: none; /* Убирает пунктирную рамку при клике и поиске */
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
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(4)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Сохраняем ссылку на QLabel имени для возможности выделения текстом
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

        # Стилизация скидки как в твоем примере
        if discount > 15:
            discount_label.setStyleSheet(
                "background-color: #2E8B57; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        else:
            discount_label.setStyleSheet(
                "background-color: #eeeeee; font-weight: bold; padding: 10px; border-radius: 5px;")

        discount_label.setFixedWidth(100)
        right_layout.addWidget(discount_label)

        # Кнопки для Администратора
        if role == "Администратор":
            right_layout.addSpacing(10)
            self.btn_edit = QPushButton("Редактировать")
            self.btn_delete = QPushButton("Удалить")
            self.btn_delete.setStyleSheet("background-color: #ffcccc; border: 1px solid #cc0000; padding: 5px;")

            self.btn_edit.clicked.connect(self.edit_me)
            self.btn_delete.clicked.connect(self.delete_me)

            right_layout.addWidget(self.btn_edit)
            right_layout.addWidget(self.btn_delete)

        elif role == "Менеджер":
            right_layout.addSpacing(10)
            self.btn_order = QPushButton("В заказ")
            right_layout.addWidget(self.btn_order)

        main_layout.addLayout(right_layout)

    def delete_me(self):
        reply = QMessageBox.question(self, 'Удаление',
                                     f"Вы действительно хотите удалить товар:\n{self.prod_name_text}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM Products WHERE ProductID = ?", (self.prod_id,))
                conn.commit()
                conn.close()
                self.hide()  # Убираем карточку с экрана
            except Exception as e:
                QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить товар: {e}")

    def edit_me(self):
        # Здесь будет вызываться твое будущее окно редактирования
        QMessageBox.information(self, "Редактирование", f"Открытие формы редактирования для:\n{self.prod_name_text}")


class ProductWindow(QWidget):
    def __init__(self, role, user_name="Гость"):
        super().__init__()
        self.role = role
        self.user_name = user_name
        self.found_cards = []
        self.current_match_index = -1
        self.setWindowTitle("Просмотр товаров")
        self.resize(1000, 700)  # Немного увеличим окно для удобства

        # Основной макет
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # --- ОБНОВЛЕННАЯ ШАПКА (ФИО справа) ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(15)

        # 1. Слева: Фильтрация
        self.filter_combo = QComboBox()
        self.filter_combo.setFixedWidth(200)
        self.filter_combo.addItems(["Все производители", "ASUS", "Lenovo", "Apple", "HP", "Samsung"])
        self.filter_combo.currentTextChanged.connect(self.load_products)
        header_layout.addWidget(self.filter_combo)

        # 2. Слева: Поиск (если не Гость)
        if self.role != "Гость":
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

        # 5. Справа: Кнопка выхода
        btn_exit = QPushButton("Выйти")
        btn_exit.setFixedWidth(80)
        btn_exit.setStyleSheet("padding: 5px; background-color: #f8f8f8; border: 1px solid #ccc;")
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
            SELECT p.*
            FROM Products p
            LEFT JOIN Manufacturers m
            ON p.ManufacturerID = m.ManufacturerID
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

    def logout(self):
        from auth_window import AuthWindow

        self.auth_win = AuthWindow()
        self.auth_win.show()
        self.close()