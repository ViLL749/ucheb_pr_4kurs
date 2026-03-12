import sys
from PyQt5.QtWidgets import QApplication
from auth_window import AuthWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_win = AuthWindow()
    login_win.show()

    sys.exit(app.exec_())