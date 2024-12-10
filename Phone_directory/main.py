import sys
from PyQt5.QtWidgets import QApplication
from database import Database
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    db = Database()
    main_win = MainWindow(db)
    main_win.show()
    exit_code = app.exec_()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
