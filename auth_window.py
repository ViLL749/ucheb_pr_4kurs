from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from db_manager import get_db_connection
from product_window import ProductWindow

class AuthWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setFixedSize(300, 220)

        layout = QVBoxLayout()

        self.label = QLabel("Авторизация")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        layout.addWidget(self.login_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Пароль")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.check_auth)
        layout.addWidget(self.btn_login)

        self.btn_guest = QPushButton("Войти как гость")
        self.btn_guest.clicked.connect(self.enter_as_guest)
        layout.addWidget(self.btn_guest)

        self.setLayout(layout)

    def check_auth(self):
        login = self.login_input.text()
        password = self.pass_input.text()

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Ищем роль пользователя по логину и паролю
            cur.execute("""
                SELECT Roles.RoleName FROM Users 
                JOIN Roles ON Users.RoleID = Roles.RoleID 
                WHERE Login=? AND Password=?""", (login, password))
            result = cur.fetchone()
            conn.close()

            # Если роль найдена, создаём окно
            if result:
                self.main_win = ProductWindow(result[0])
                self.main_win.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))

    def enter_as_guest(self):
        # Логика гостя
        self.main_win = ProductWindow("Гость")
        self.main_win.show()
        self.close()