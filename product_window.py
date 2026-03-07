from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QFrame, QPushButton)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from db_manager import get_db_connection


class ProductCard(QFrame):
    def __init__(self, product_data, role):
        super().__init__()

        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet("background:white;")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # 1 Левая часть (фото)

        photo_block = QVBoxLayout()

        photo_label = QLabel()
        photo_label.setFixedSize(160,160)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("border:1px solid gray;")

        photo_filename = str(product_data[9]).strip()
        pixmap = QPixmap(f"photo/{photo_filename}")

        if pixmap.isNull():
            photo_label.setText("Фото")
        else:
            photo_label.setPixmap(
                pixmap.scaled(140,140,Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        photo_block.addWidget(photo_label)
        main_layout.addLayout(photo_block)

        # 2 Центр (информация)

        center_layout = QVBoxLayout()
        center_layout.setSpacing(4)

        center_layout.addWidget(QLabel(f"Наименование: {product_data[1]}"))
        center_layout.addWidget(QLabel(f"Категория: {product_data[2]}"))
        center_layout.addWidget(QLabel(f"Производитель: {product_data[3]}"))
        center_layout.addWidget(QLabel(f"Поставщик: {product_data[4]}"))

        center_layout.addWidget(QLabel(f"Цена: {product_data[5]} р"))
        center_layout.addWidget(QLabel(f"Гарантия: {product_data[10]} мес"))
        center_layout.addWidget(QLabel(f"Количество: {product_data[7]} шт"))

        main_layout.addLayout(center_layout, stretch=1)

        # 3 Правая часть (скидка)

        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)

        discount = product_data[6]

        discount_label = QLabel(f"Скидка: {discount}%")
        discount_label.setStyleSheet("font-size:16px;")

        right_layout.addWidget(discount_label)

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)


        # # 4 Панель действий (по роли)
        # actions_layout = QHBoxLayout()
        #
        # if role == "Администратор":
        #     btn_edit = QPushButton("Редактировать")
        #     btn_delete = QPushButton("Удалить")
        #     btn_delete.setStyleSheet("background-color: #ffcccc;")
        #     actions_layout.addWidget(btn_edit)
        #     actions_layout.addWidget(btn_delete)
        #
        # elif role == "Менеджер":
        #     btn_order = QPushButton("В заказ")
        #     actions_layout.addWidget(btn_order)

        # Для Гостя/Клиента кнопок нет
        center_layout.addLayout(actions_layout)

class ProductWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.setWindowTitle("Просмотр товаров")
        self.resize(800, 600)

        main_layout = QVBoxLayout()

        # Шапка
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"Роль: <b>{self.role}</b>"))
        # Кнопка выход
        btn_exit = QPushButton("Выйти")
        btn_exit.setFixedWidth(80)
        btn_exit.clicked.connect(self.logout)
        header_layout.addWidget(btn_exit)
        main_layout.addLayout(header_layout)

        # Скролл
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.content_layout = QVBoxLayout(scroll_content)
        self.content_layout.setAlignment(Qt.AlignTop)

        self.load_products()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def load_products(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Products")
            products = cur.fetchall()
            conn.close()

            for prod in products:
                self.content_layout.addWidget(ProductCard(prod, self.role))
        except Exception as e:
            print(f"Ошибка: {e}")


    def logout(self):
        from auth_window import AuthWindow

        self.auth_win = AuthWindow()
        self.auth_win.show()
        self.close()