import sys
import time
import json
import sqlite3
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class FetchWorker(QThread):
    data_fetched = pyqtSignal(list)  # Signal to emit fetched data
    error_occurred = pyqtSignal(str)  # Signal for errors

    def run(self):
        try:
            time.sleep(2)  # Add delay to simulate longer request
            response = requests.get('https://jsonplaceholder.typicode.com/posts')
            response.raise_for_status()
            data = response.json()
            self.data_fetched.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))

class SaveWorker(QThread):
    data_saved = pyqtSignal()  # Signal when data is saved
    error_occurred = pyqtSignal(str)  # Signal for errors

    def __init__(self, data, db_name='posts.db'):
        super().__init__()
        self.data = data
        self.db_name = db_name

    def run(self):
        try:
            # Simulate delay
            time.sleep(2)  # Add delay to simulate longer save operation
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY,
                    userId INTEGER,
                    title TEXT,
                    body TEXT
                )
            ''')
            # Insert or update data
            for post in self.data:
                cursor.execute('''
                    INSERT OR REPLACE INTO posts (id, userId, title, body)
                    VALUES (?, ?, ?, ?)
                ''', (post['id'], post['userId'], post['title'], post['body']))
            conn.commit()
            conn.close()
            self.data_saved.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Loader')
        self.layout = QVBoxLayout()

        self.load_button = QPushButton('Загрузить данные')
        self.load_button.clicked.connect(self.start_fetch)
        self.layout.addWidget(self.load_button)

        self.status_label = QLabel('Статус: Готов')
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_fetch)
        self.timer.start(10000)  # Every 10 seconds

        self.db_name = 'posts.db'

    def start_fetch(self):
        self.status_label.setText('Статус: Загрузка данных...')
        self.progress_bar.show()
        self.load_button.setEnabled(False)
        self.fetch_worker = FetchWorker()
        self.fetch_worker.data_fetched.connect(self.on_data_fetched)
        self.fetch_worker.error_occurred.connect(self.on_error)
        self.fetch_worker.start()

    def on_data_fetched(self, data):
        self.status_label.setText('Статус: Сохранение данных...')
        self.save_worker = SaveWorker(data, self.db_name)
        self.save_worker.data_saved.connect(self.on_data_saved)
        self.save_worker.error_occurred.connect(self.on_error)
        self.save_worker.start()

    def on_data_saved(self):
        self.status_label.setText('Статус: Данные сохранены')
        self.progress_bar.hide()
        self.load_button.setEnabled(True)
        self.update_display()

    def on_error(self, error_msg):
        self.status_label.setText(f'Статус: Ошибка - {error_msg}')
        self.progress_bar.hide()
        self.load_button.setEnabled(True)

    def update_display(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM posts LIMIT 10')  # Display first 10 for brevity
            rows = cursor.fetchall()
            conn.close()
            display_text = ''
            for row in rows:
                display_text += f'ID: {row[0]}, UserID: {row[1]}, Title: {row[2]}, Body: {row[3]}\n\n'
            self.text_edit.setText(display_text)
        except Exception as e:
            self.status_label.setText(f'Статус: Ошибка при отображении - {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
