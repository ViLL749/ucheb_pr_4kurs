from tkinter.ttk import Combobox

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QPushButton, QTextEdit, QSpinBox, QDoubleSpinBox,
                             QMessageBox, QHBoxLayout, QComboBox)
from db_manager import get_db_connection


class ProductForm(QDialog):
    def __init__(self, product_data=None):
        super().__init__()


        self.old_data = product_data
        self.product_data = product_data
        self.setWindowTitle("Добавление товара" if not product_data else "Редактирование товара")
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.article = QLineEdit()
        self.name = QLineEdit()

        self.category = QComboBox()
        self.category.setMaxCount(9999)

        self.manufacturer = QComboBox()
        self.manufacturer.setMaxCount(9999)

        self.supplier = QComboBox()
        self.supplier.setMaxCount(9999)

        self.price = QDoubleSpinBox()
        self.price.setMaximum(10000000)

        self.discount = QSpinBox()
        self.discount.setMaximum(100)

        self.quantity = QSpinBox()
        self.quantity.setMaximum(100000)

        self.description = QTextEdit()

        self.photo = QLineEdit()

        self.warranty = QSpinBox()
        self.warranty.setMaximum(120)

        form.addRow("Артикул", self.article)
        form.addRow("Название", self.name)
        form.addRow("Категория", self.category)
        form.addRow("Производитель", self.manufacturer)
        form.addRow("Поставщик", self.supplier)
        form.addRow("Цена", self.price)
        form.addRow("Скидка %", self.discount)
        form.addRow("Количество", self.quantity)
        form.addRow("Описание", self.description)
        form.addRow("Фото (имя файла)", self.photo)
        form.addRow("Гарантия (мес)", self.warranty)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()




        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")


        self.btn_save.setStyleSheet("""
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
        self.btn_cancel.setStyleSheet("""
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



        # Общий стиль
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
                font-size: 12pt;
            }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-family: 'Times New Roman';
                padding: 6px;
                min-height: 28px;       
                min-width: 200px;      
            }
            QTextEdit {
                min-height: 80px;      
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                selection-background-color: #00FA9A;
                selection-color: black;   
            }
        """)


        self.article.setMinimumWidth(220)
        self.name.setMinimumWidth(220)
        self.photo.setMinimumWidth(220)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        self.btn_save.clicked.connect(self.save_product)
        self.btn_cancel.clicked.connect(self.close)

        if product_data:
            self.load_data()

        self.load_comboboxes()



    def set_combo_value(self, combo, value):

        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def load_data(self):

        p = self.product_data

        self.article.setText(str(p[0]))
        self.name.setText(str(p[1]))

        self.set_combo_value(self.category, p[2])
        self.set_combo_value(self.manufacturer, p[3])
        self.set_combo_value(self.supplier, p[4])

        self.price.setValue(p[5])
        self.discount.setValue(p[6])
        self.quantity.setValue(p[7])
        self.description.setText(str(p[8]))
        self.photo.setText(str(p[9]))
        self.warranty.setValue(p[10])

    def save_product(self):

        from logger import log_product

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            data = (
                self.article.text(),
                self.name.text(),
                self.category.currentData(),
                self.manufacturer.currentData(),
                self.supplier.currentData(),
                self.price.value(),
                self.discount.value(),
                self.quantity.value(),
                self.description.toPlainText(),
                self.photo.text(),
                self.warranty.value()
            )

            details = ""

            # Если редактирование
            if self.old_data:

                fields = [
                    ("Название", self.old_data[1], self.name.text()),
                    ("Цена", self.old_data[5], self.price.value()),
                    ("Скидка", self.old_data[6], self.discount.value()),
                    ("Количество", self.old_data[7], self.quantity.value()),
                    ("Гарантия", self.old_data[10], self.warranty.value())
                ]

                for field, old, new in fields:
                    if str(old) != str(new):
                        details += f"{field}: {old} → {new}\n"

                cur.execute("""
                UPDATE Products SET
                ProductName=?,
                CategoryID=?,
                ManufacturerID=?,
                SupplierID=?,
                Price=?,
                Discount=?,
                QuantityInStock=?,
                Description=?,
                Photo=?,
                WarrantyMonths=?
                WHERE Article=?
                """, (
                    data[1], data[2], data[3], data[4],
                    data[5], data[6], data[7], data[8],
                    data[9], data[10], data[0]
                ))

                log_product(
                    cur,
                    "Изменение",
                    data[0],
                    data[1],
                    "admin",
                    details
                )

            # Если добавление
            else:

                cur.execute("""
                INSERT INTO Products
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, data)

                log_product(
                    cur,
                    "Добавление",
                    data[0],
                    data[1],
                    "admin"
                )

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Товар сохранён")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def load_comboboxes(self):

        conn = get_db_connection()
        cur = conn.cursor()

        # категории
        cur.execute("SELECT CategoryID, CategoryName FROM Categories")
        for row in cur.fetchall():
            self.category.addItem(row[1], row[0])

        # производители
        cur.execute("SELECT ManufacturerID, ManufacturerName FROM Manufacturers")
        for row in cur.fetchall():
            self.manufacturer.addItem(row[1], row[0])

        # поставщики
        cur.execute("SELECT SupplierID, SupplierName FROM Suppliers")
        for row in cur.fetchall():
            self.supplier.addItem(row[1], row[0])

        conn.close()