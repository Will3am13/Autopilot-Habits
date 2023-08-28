import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLineEdit, QListView, QPushButton


class TodoListWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.current_tasks = []
        self.completed_tasks = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.task_input = QLineEdit()
        self.task_input.setFrame(False)
        self.task_input.setStyleSheet("""
            QLineEdit {
                border-radius: 10px;
                background-color: #333333;
                color: #ffffff;
                font-size: 20px;
                padding: 8px;
            }
        """)
        self.layout.addWidget(self.task_input)

        self.add_button = QPushButton("Add Task")
        self.add_button.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
        self.add_button.setStyleSheet("""
            QPushButton {
                border-radius: 10px;
                background-color: #333333;
                color: #ffffff;
                font-size: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.layout.addWidget(self.add_button)

        self.tasks_model = QStandardItemModel()
        self.task_list = QListView()
        self.task_list.setModel(self.tasks_model)
        self.task_list.clicked.connect(self.toggle_task)
        self.task_list.doubleClicked.connect(self.remove_task)
        self.task_list.setStyleSheet("""
            QListView {
                border-radius: 10px;
                background-color: #333333;
                color: #ffffff;
                font-size: 20px;
                outline: none;
                padding: 8px;
            }
            QListView::item:hover {
                background-color: #555555;
            }
        """)
        self.layout.addWidget(self.task_list)

        self.clear_button = QPushButton("Clear Tasks")
        self.clear_button.clicked.connect(self.clear_tasks)
        self.clear_button.setStyleSheet("""
                    QPushButton {
                        border-radius: 10px;
                        background-color: #333333;
                        color: #ffffff;
                        font-size: 20px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #555555;
                    }
                    QListView::item:selected {
                        background-color: #555555;  /* Remove the selection effect */
                    }
                    QListView::item:focus {
                        outline: none;  /* Remove the focus outline */
                    }
                """)
        self.layout.addWidget(self.clear_button)

    def add_task(self):
        task_text = self.task_input.text()
        if task_text:
            item = QStandardItem(task_text)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.current_tasks.append(item)
            self.tasks_model.appendRow(item)
            self.task_input.clear()

    def toggle_task(self, index):
        item = self.tasks_model.itemFromIndex(index)
        if item in self.current_tasks:
            self.current_tasks.remove(item)
            self.completed_tasks.append(item)
            item.setBackground(Qt.transparent)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
        else:
            self.completed_tasks.remove(item)
            self.current_tasks.append(item)
            item.setBackground(Qt.transparent)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setFlags(item.flags() | Qt.ItemIsSelectable)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            font = item.font()
            font.setStrikeOut(False)
            item.setFont(font)

        self.task_list.clearSelection()  # Clear selection after toggling

    def remove_task(self, index):
        item = self.tasks_model.itemFromIndex(index)
        if item in self.current_tasks:
            self.current_tasks.remove(item)
        else:
            self.completed_tasks.remove(item)
        self.tasks_model.removeRow(index.row())

    def clear_tasks(self):
        self.current_tasks = []
        self.completed_tasks = []
        self.tasks_model.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = TodoListWidget()
    widget.setStyleSheet("background-color: #202020; color: #ffffff;")
    widget.resize(400, 500)  # Adjust the desired size of the application
    widget.show()
    sys.exit(app.exec())
