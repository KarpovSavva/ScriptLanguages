import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLineEdit, QLabel, QDialog, QFormLayout,
    QSpinBox, QTextEdit, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel


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
        self.setWindowTitle("Управление записями")
        self.resize(800, 600)

        self.db = None
        self.model = None
        self.proxy_model = None

        self.init_db()
        self.init_ui()

    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("posts.db")  # Убедитесь, что файл posts.db существует

        if not self.db.open():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных!")
            sys.exit(1)

        if "posts" not in self.db.tables():
            QMessageBox.critical(self, "Ошибка", "Таблица 'posts' не найдена в базе данных!")
            sys.exit(1)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск по заголовку:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
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
        self.model.select()

        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "User ID")
        self.model.setHeaderData(2, Qt.Horizontal, "Title")
        self.model.setHeaderData(3, Qt.Horizontal, "Body")

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(2)  # Фильтр по колонке Title
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.table_view.setModel(self.proxy_model)

    def filter_table(self):
        search_text = self.search_input.text()
        self.proxy_model.setFilterFixedString(search_text)

    def refresh_table(self):
        self.model.select()
        self.filter_table()

    def add_record(self):
        dialog = AddRecordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_id, title, body = dialog.get_data()
            if not title or not body:
                QMessageBox.warning(self, "Ошибка", "Title и Body пустые")
                return

            record = self.model.record()
            record.setValue("userId", user_id)
            record.setValue("title", title)
            record.setValue("body", body)

            if self.model.insertRecord(-1, record):
                self.model.submitAll()
                self.refresh_table()
                QMessageBox.information(self, "Успех", "Запись успешно добавлена!")
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{self.model.lastError().text()}")

    def delete_record(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            row = selected[0].row()
            proxy_index = self.proxy_model.index(row, 0)
            source_index = self.proxy_model.mapToSource(proxy_index)
            if self.model.removeRow(source_index.row()):
                self.model.submitAll()
                self.refresh_table()
                QMessageBox.information(self, "Успех", "Запись успешно удалена!")
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись:\n{self.model.lastError().text()}")


    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
