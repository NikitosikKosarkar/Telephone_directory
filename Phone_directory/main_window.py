from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QDialog,
    QLineEdit, QHeaderView, QHBoxLayout, QLabel, QGroupBox, QGridLayout, QSizePolicy, QMessageBox,
)
from manage_parent_dialog import ManageParentDialog
from utils_dialog import UtilsDialog


class MainWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Телефонный справочник")
        self.resize(1400, 800)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        search_group = QGroupBox("Поиск")
        search_layout = QHBoxLayout()
        search_group.setLayout(search_layout)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Общий поиск...")
        self.search_input.textChanged.connect(self.search)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_input)
        self.top_layout.addWidget(search_group)

        manage_group = QGroupBox("Управление таблицами")
        manage_layout = QHBoxLayout()
        manage_group.setLayout(manage_layout)

        self.manage_surnames_button = QPushButton("Фамилии")
        self.manage_surnames_button.clicked.connect(lambda: self.show_manage_dialog('surnames', 'Фамилии'))
        manage_layout.addWidget(self.manage_surnames_button)

        self.manage_names_button = QPushButton("Имена")
        self.manage_names_button.clicked.connect(lambda: self.show_manage_dialog('names', 'Имена'))
        manage_layout.addWidget(self.manage_names_button)

        self.manage_patronymics_button = QPushButton("Отчества")
        self.manage_patronymics_button.clicked.connect(lambda: self.show_manage_dialog('patronymics', 'Отчества'))
        manage_layout.addWidget(self.manage_patronymics_button)

        self.top_layout.addWidget(manage_group)

        self.top_layout.addStretch()

        filters_group = QGroupBox("Фильтры по столбцам")
        filters_layout = QGridLayout()
        filters_group.setLayout(filters_layout)
        self.filter_widgets = {}
        headers = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Город', 'Улица', 'Дом', 'Телефон']
        for col, header in enumerate(headers):
            label = QLabel(header)
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Фильтр {header}")
            line_edit.textChanged.connect(self.apply_column_filters)
            self.filter_widgets[header] = line_edit
            filters_layout.addWidget(label, 0, col)
            filters_layout.addWidget(line_edit, 1, col)
        self.layout.addWidget(filters_group)

        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Фамилия', 'Имя', 'Отчество',
            'Город', 'Улица', 'Дом', 'Телефон'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)

        self.layout.addWidget(self.table)

        self.utils_button = QPushButton("Utils")
        self.utils_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.utils_button.clicked.connect(self.show_utils_dialog)
        self.layout.addWidget(self.utils_button, alignment=Qt.AlignRight)

        self.update_table()

        self.filter_timer = QTimer()
        self.filter_timer.setInterval(300)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_column_filters)

    def update_table(self):
        query = """
            SELECT d.uid, s.value AS surname, n.value AS name, p.value AS patronymic,
                   d.city, d.street, d.house, d.telephone
            FROM directory d
            JOIN surnames s ON d.surname = s.uid
            JOIN names n ON d.name = n.uid
            JOIN patronymics p ON d.patronymic = p.uid;
        """
        rows = self.db.fetch_all(query)
        self.display_rows(rows)

    def display_rows(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

    def search(self):
        self.search_input.text().strip()
        self.filter_timer.start()

    def apply_column_filters(self):
        filters = {}
        for header, widget in self.filter_widgets.items():
            text = widget.text().strip()
            if text:
                filters[header] = text

        search_term = self.search_input.text().strip()

        base_query = """
            SELECT d.uid, s.value AS surname, n.value AS name, p.value AS patronymic,
                   d.city, d.street, d.house, d.telephone
            FROM directory d
            JOIN surnames s ON d.surname = s.uid
            JOIN names n ON d.name = n.uid
            JOIN patronymics p ON d.patronymic = p.uid
        """
        conditions = []
        params = []

        if search_term:
            conditions.append("""
                (s.value ILIKE %s
                OR n.value ILIKE %s
                OR p.value ILIKE %s
                OR d.city ILIKE %s
                OR d.street ILIKE %s
                OR d.house::text ILIKE %s
                OR d.telephone ILIKE %s)
            """)
            like_term = f'%{search_term}%'
            params.extend([like_term] * 7)

        header_to_field = {
            'ID': 'd.uid',
            'Фамилия': 's.value',
            'Имя': 'n.value',
            'Отчество': 'p.value',
            'Город': 'd.city',
            'Улица': 'd.street',
            'Дом': 'd.house::text',
            'Телефон': 'd.telephone'
        }

        for header, value in filters.items():
            field = header_to_field.get(header, None)
            if field:
                conditions.append(f"{field} ILIKE %s")
                params.append(f'%{value}%')

        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
        else:
            where_clause = ""

        final_query = base_query + where_clause + ";"

        try:
            rows = self.db.fetch_all(final_query, params)
            self.display_rows(rows)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить фильтрацию:\n{e}")
            print("[ERROR] Failed to apply filters")

    def show_utils_dialog(self):
        dialog = UtilsDialog(self.db)
        if dialog.exec_() == QDialog.Accepted:
            self.update_table()

    def show_manage_dialog(self, table_name, title):
        dialog = ManageParentDialog(self.db, table_name, title)
        if dialog.exec_() == QDialog.Accepted:
            self.update_table()
