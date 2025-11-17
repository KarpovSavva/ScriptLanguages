import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLineEdit, QLabel, QDialog, QFormLayout,
    QSpinBox, QTextEdit, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery


class AddRecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")
        self.setModal(True)

        self.layout = QFormLayout()

        self.user_id_input = QSpinBox()
        self.user_id_input.setRange(1, 1000)

        self.title_input = QLineEdit()
        self.body_input = QTextEdit()
        self.body_input.setFixedHeight(100)

        self.layout.addRow("User ID:", self.user_id_input)
        self.layout.addRow("Title:", self.title_input)
        self.layout.addRow("Body:", self.body_input)

        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Добавить")
        self.cancel_button = QPushButton("Отмена")

        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addRow(self.button_layout)
        self.setLayout(self.layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_data(self):
        return (
            self.user_id_input.value(),
            self.title_input.text().strip(),
            self.body_input.toPlainText().strip()
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление записями (SQLite + PyQt5)")
        self.resize(900, 600)

        self.db = None
        self.model = None
        self.proxy_model = None

        self.init_db()
        self.init_ui()

    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("posts.db") 

        if not self.db.open():
            error = self.db.lastError().text()
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось открыть БД:\n{error}")
            sys.exit(1)

        query = QSqlQuery(self.db)
        if not query.exec_("PRAGMA table_info(posts);"):
            QMessageBox.critical(self, "Ошибка", "Таблица 'posts' не найдена!")
            sys.exit(1)

        columns = []
        while query.next():
            columns.append(query.value(1)) 

        required = ['id', 'userId', 'title', 'body']
        missing = [col for col in required if col not in columns]
        if missing:
            QMessageBox.critical(
                self, "Ошибка структуры",
                f"Отсутствуют колонки в таблице 'posts': {', '.join(missing)}\n"
                f"Доступные: {', '.join(columns)}"
            )
            sys.exit(1)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск по заголовку:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст...")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_view)

        buttons_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.add_btn = QPushButton("Добавить")
        self.delete_btn = QPushButton("Удалить")

        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setup_model()

        self.search_input.textChanged.connect(self.filter_table)
        self.refresh_btn.clicked.connect(self.refresh_table)
        self.add_btn.clicked.connect(self.add_record)
        self.delete_btn.clicked.connect(self.delete_record)

    def setup_model(self):
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable("posts")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)

        # Устанавливаем заголовки вручную
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "User ID")
        self.model.setHeaderData(2, Qt.Horizontal, "Title")
        self.model.setHeaderData(3, Qt.Horizontal, "Body")

        if not self.model.select():
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{self.model.lastError().text()}")

        # Прокси для фильтрации
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(2)  
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.table_view.setModel(self.proxy_model)

    def filter_table(self):
        text = self.search_input.text().strip()
        self.proxy_model.setFilterFixedString(text)

    def refresh_table(self):
        self.model.select()
        while self.model.canFetchMore():
            self.model.fetchMore()
        self.filter_table()

    def add_record(self):
        dialog = AddRecordDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        user_id, title, body = dialog.get_data()
        if not title or not body:
            QMessageBox.warning(self, "Ошибка", "Title и Body обязательны!")
            return

        # Создаём запись
        record = self.model.record()
        record.setValue("userId", user_id)
        record.setValue("title", title)
        record.setValue("body", body)

        # Вставляем в конец
        row = self.model.rowCount()
        if self.model.insertRow(row):
            self.model.setRecord(row, record)
            if self.model.submitAll():
                self.refresh_table()
                QMessageBox.information(self, "Успех", "Запись добавлена!")
            else:
                self.model.revertAll()
                error = self.model.lastError().text()
                QMessageBox.critical(self, "Ошибка добавления", f"Не удалось сохранить:\n{error}")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось вставить строку.")

    def delete_record(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        proxy_row = indexes[0].row()
        source_row = self.proxy_model.mapToSource(self.proxy_model.index(proxy_row, 0)).row()

        if self.model.removeRow(source_row):
            if self.model.submitAll():
                self.refresh_table()
                QMessageBox.information(self, "Успех", "Запись удалена!")
            else:
                self.model.revertAll()
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{self.model.lastError().text()}")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось удалить строку.")

    def closeEvent(self, event):
        if self.db and self.db.isOpen():
            self.db.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())