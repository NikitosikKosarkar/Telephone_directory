from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLineEdit, QLabel, QHeaderView
)
from PyQt5.QtCore import Qt


class ManageParentDialog(QDialog):
    def __init__(self, db, table_name, title):
        super().__init__()
        self.db = db
        self.table_name = table_name
        self.setWindowTitle(f"Управление {title}")
        self.resize(600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['UID', 'Value'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.form_layout = QHBoxLayout()

        self.value_label = QLabel("Value:", self)
        self.form_layout.addWidget(self.value_label)

        self.value_input = QLineEdit(self)
        self.form_layout.addWidget(self.value_input)

        self.layout.addLayout(self.form_layout)

        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_entry)
        self.buttons_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Обновить", self)
        self.update_button.clicked.connect(self.update_entry)
        self.buttons_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_entry)
        self.buttons_layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton("Обновить Таблицу", self)
        self.refresh_button.clicked.connect(self.load_data)
        self.buttons_layout.addWidget(self.refresh_button)

        self.layout.addLayout(self.buttons_layout)

        self.load_data()

    def load_data(self):
        query = f"SELECT uid, value FROM {self.table_name} ORDER BY uid ASC;"
        rows = self.db.fetch_all(query)
        self.table.setRowCount(len(rows))

        for row_idx, row_data in enumerate(rows):
            uid_item = QTableWidgetItem(str(row_data[0]))
            uid_item.setFlags(uid_item.flags() ^ Qt.ItemIsEditable)
            value_item = QTableWidgetItem(str(row_data[1]))
            value_item.setFlags(value_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row_idx, 0, uid_item)
            self.table.setItem(row_idx, 1, value_item)

    def add_entry(self):
        value = self.value_input.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите значение.")
            print("[ERROR] No value entered")
            return

        query = f"INSERT INTO {self.table_name} (value) VALUES (%s) RETURNING uid;"
        try:
            self.db.execute_query(query, (value,))
            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            print("[DEBUG] The entry was successfully added")
            self.load_data()
            self.value_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{e}")
            print("[ERROR] Failed to add an entry")

    def update_entry(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите запись для обновления.")
            print("[ERROR] No entry selected for update")
            return

        uid = selected_items[0].text()
        new_value = self.value_input.text().strip()
        if not new_value:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите новое значение.")
            print("[ERROR] No new value entered")
            return

        query = f"UPDATE {self.table_name} SET value = %s WHERE uid = %s;"
        try:
            self.db.execute_query(query, (new_value, uid))
            QMessageBox.information(self, "Успех", "Запись успешно обновлена!")
            print("[DEBUG] The entry was successfully updated")
            self.load_data()
            self.value_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись:\n{e}")
            print("[ERROR] Failed to update an entry")

    def delete_entry(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите запись для удаления.")
            print("[ERROR] No entry selected for deletion")
            return

        uid = selected_items[0].text()
        value = selected_items[1].text()
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить запись:\nUID: {uid}\nValue: {value}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            query = f"DELETE FROM {self.table_name} WHERE uid = %s;"
            try:
                self.db.execute_query(query, (uid,))
                QMessageBox.information(self, "Успех", "Запись успешно удалена!")
                print("[DEBUG] The entry was successfully deleted")
                self.load_data()
                self.value_input.clear()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись:\n{e}")
                print("[ERROR] Failed to delete an entry")
