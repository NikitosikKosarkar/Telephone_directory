from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout
)
from psycopg2 import sql


class UtilsDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Utils")
        self.resize(400, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()

        self.id_input = QLineEdit(self)
        self.surname_input = QLineEdit(self)
        self.name_input = QLineEdit(self)
        self.patronymic_input = QLineEdit(self)
        self.city_input = QLineEdit(self)
        self.street_input = QLineEdit(self)
        self.house_input = QLineEdit(self)
        self.telephone_input = QLineEdit(self)

        self.form_layout.addRow('ID (For Update/Delete):', self.id_input)
        self.form_layout.addRow('Фамилия:', self.surname_input)
        self.form_layout.addRow('Имя:', self.name_input)
        self.form_layout.addRow('Отчество:', self.patronymic_input)
        self.form_layout.addRow('Город:', self.city_input)
        self.form_layout.addRow('Улица:', self.street_input)
        self.form_layout.addRow('Дом:', self.house_input)
        self.form_layout.addRow('Телефон:', self.telephone_input)

        self.layout.addLayout(self.form_layout)

        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_record)

        self.update_button = QPushButton("Update", self)
        self.update_button.clicked.connect(self.update_record)

        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_record)

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.update_button)
        self.buttons_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.buttons_layout)

    def add_record(self):
        surname = self.surname_input.text().strip()
        name = self.name_input.text().strip()
        patronymic = self.patronymic_input.text().strip()
        city = self.city_input.text().strip()
        street = self.street_input.text().strip()
        house = self.house_input.text().strip()
        telephone = self.telephone_input.text().strip()

        if not all([surname, name, patronymic, city, street, house, telephone]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            print("[ERROR] Not all fields are filled in")
            return

        surname_uid = self.get_or_create_uid('surnames', surname)
        name_uid = self.get_or_create_uid('names', name)
        patronymic_uid = self.get_or_create_uid('patronymics', patronymic)

        query = """
            INSERT INTO directory (surname, name, patronymic, city, street, house, telephone)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (surname_uid, name_uid, patronymic_uid, city, street, house, telephone)

        try:
            self.db.execute_query(query, params)
            QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            print("[DEBUG] The entry was successfully added")
            self.clear_fields()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{e}")
            print("[ERROR] Failed to add an entry")

    def update_record(self):
        uid = self.id_input.text().strip()
        if not uid:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите ID для обновления.")
            print("[ERROR] The update id has not been entered")
            return

        surname = self.surname_input.text().strip()
        name = self.name_input.text().strip()
        patronymic = self.patronymic_input.text().strip()
        city = self.city_input.text().strip()
        street = self.street_input.text().strip()
        house = self.house_input.text().strip()
        telephone = self.telephone_input.text().strip()

        if not all([surname, name, patronymic, city, street, house, telephone]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            print("[ERROR] Not all fields are filled in")
            return

        surname_uid = self.get_or_create_uid('surnames', surname)
        name_uid = self.get_or_create_uid('names', name)
        patronymic_uid = self.get_or_create_uid('patronymics', patronymic)

        query = """
            UPDATE directory
            SET surname = %s,
                name = %s,
                patronymic = %s,
                city = %s,
                street = %s,
                house = %s,
                telephone = %s
            WHERE uid = %s;
        """
        params = (surname_uid, name_uid, patronymic_uid, city, street, house, telephone, uid)

        try:
            self.db.execute_query(query, params)
            QMessageBox.information(self, "Успех", "Запись успешно обновлена!")
            print("[DEBUG] The entry was successfully updated")
            self.clear_fields()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись:\n{e}")
            print("[ERROR] Failed to update an entry")

    def delete_record(self):
        uid = self.id_input.text().strip()
        if not uid:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите ID для удаления.")
            print("[ERROR] The delete id has not been entered")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить запись с ID {uid}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            query = "DELETE FROM directory WHERE uid = %s;"
            try:
                self.db.execute_query(query, (uid,))
                QMessageBox.information(self, "Успех", "Запись успешно удалена!")
                print("[DEBUG] The entry was successfully deleted")
                self.clear_fields()
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись:\n{e}")
                print("[ERROR] Failed to delete an entry")

    def get_or_create_uid(self, table, value):
        select_query = sql.SQL("SELECT uid FROM {table} WHERE value = %s;").format(
            table=sql.Identifier(table)
        )
        self.db.cursor.execute(select_query, (value,))
        result = self.db.cursor.fetchone()
        if result:
            return result[0]
        else:
            insert_query = sql.SQL("INSERT INTO {table} (value) VALUES (%s) RETURNING uid;").format(
                table=sql.Identifier(table)
            )
            self.db.cursor.execute(insert_query, (value,))
            self.db.conn.commit()
            return self.db.cursor.fetchone()[0]

    def clear_fields(self):
        self.id_input.clear()
        self.surname_input.clear()
        self.name_input.clear()
        self.patronymic_input.clear()
        self.city_input.clear()
        self.street_input.clear()
        self.house_input.clear()
        self.telephone_input.clear()
