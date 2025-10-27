import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTextEdit, QComboBox, QFileDialog, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Visualization App")
        self.setGeometry(100, 100, 800, 600)

        self.df = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.load_button = QPushButton("Загрузить данные из CSV")
        self.load_button.clicked.connect(self.load_data)
        main_layout.addWidget(self.load_button)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        main_layout.addWidget(QLabel("Статистика по данным:"))
        main_layout.addWidget(self.stats_text)

        self.graph_combo = QComboBox()
        self.graph_combo.addItems(["Линейный график", "Гистограмма", "Круговая диаграмма"])
        self.graph_combo.currentIndexChanged.connect(self.update_graph)
        main_layout.addWidget(QLabel("Тип визуализации:"))
        main_layout.addWidget(self.graph_combo)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(QLabel("График:"))
        main_layout.addWidget(self.canvas)

        add_layout = QHBoxLayout()
        main_layout.addLayout(add_layout)

        add_layout.addWidget(QLabel("Date:"))
        self.date_input = QLineEdit()
        add_layout.addWidget(self.date_input)

        add_layout.addWidget(QLabel("Value1:"))
        self.value1_input = QLineEdit()
        add_layout.addWidget(self.value1_input)

        add_layout.addWidget(QLabel("Value2:"))
        self.value2_input = QLineEdit()
        add_layout.addWidget(self.value2_input)

        add_layout.addWidget(QLabel("Category:"))
        self.category_input = QLineEdit()
        add_layout.addWidget(self.category_input)

        self.add_button = QPushButton("Добавить значение")
        self.add_button.clicked.connect(self.add_data)
        add_layout.addWidget(self.add_button)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть CSV файл", "", "CSV files (*.csv)")
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.update_stats()
                self.update_graph()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def update_stats(self):
        if self.df is not None:
            stats = []
            stats.append(f"Количество строк: {len(self.df)}")
            stats.append(f"Количество столбцов: {len(self.df.columns)}")

            numeric_cols = self.df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                stats.append(f"{col} - Мин: {self.df[col].min()}, Макс: {self.df[col].max()}")
                stats.append(f"{col} - Среднее: {self.df[col].mean():.2f}, Медиана: {self.df[col].median():.2f}")

            self.stats_text.setText("\n".join(stats))

    def update_graph(self):
        if self.df is None:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        graph_type = self.graph_combo.currentText()

        try:
            if graph_type == "Линейный график":
                # Assuming Date is sortable, convert to datetime if needed
                self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
                sorted_df = self.df.sort_values('Date')
                ax.plot(sorted_df['Date'], sorted_df['Value1'])
                ax.set_title("Линейный график (Date vs Value1)")
                ax.set_xlabel("Date")
                ax.set_ylabel("Value1")
                plt.xticks(rotation=45)

            elif graph_type == "Гистограмма":
                # Interpreting as bar plot for Date vs Value2
                self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
                sorted_df = self.df.sort_values('Date')
                sns.barplot(x=sorted_df['Date'], y=sorted_df['Value2'], ax=ax)
                ax.set_title("Гистограмма (Date vs Value2)")
                ax.set_xlabel("Date")
                ax.set_ylabel("Value2")
                plt.xticks(rotation=45)

            elif graph_type == "Круговая диаграмма":
                category_counts = self.df['Category'].value_counts()
                ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
                ax.set_title("Круговая диаграмма (Category)")

            self.canvas.draw()
        except KeyError as e:
            QMessageBox.warning(self, "Ошибка", f"Отсутствует столбец: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось построить график: {str(e)}")

    def add_data(self):
        if self.df is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные.")
            return

        try:
            date = self.date_input.text()
            value1 = float(self.value1_input.text())
            value2 = float(self.value2_input.text())
            category = self.category_input.text()

            new_row = pd.DataFrame({
                'Date': [date],
                'Value1': [value1],
                'Value2': [value2],
                'Category': [category]
            })
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            self.update_stats()
            self.update_graph()

            self.date_input.clear()
            self.value1_input.clear()
            self.value2_input.clear()
            self.category_input.clear()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат значений Value1 или Value2 (должны быть числами).")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
