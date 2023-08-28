import sys
from PySide6.QtCore import Qt, QDateTime, Signal, QTime, QTimer
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QDialog, \
    QFormLayout, QLineEdit, QDateTimeEdit, QMessageBox, QColorDialog, QCheckBox
from PySide6.QtGui import QColor, QBrush
import openai
from datetime import datetime
from hostBlocking import WebsiteBlocking

# Set up your OpenAI API credentials
openai.api_key = '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'


class ScheduleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.create_table()
        self.create_add_event_button()
        self.create_auto_scheduler_button()
        self.create_toggleBlock_button()
        self.start_timer()
        self.events = []

    def create_table(self):
        self.table = QTableWidget()

        # Set the number of rows and columns
        self.table.setRowCount(289)  # 24 hours * 60 minutes / 5 minutes = 288 + 1 for 12:00 AM
        self.table.setColumnCount(7)  # 7 days

        # Set the vertical header labels (time)
        for row in range(289):
            hour = (row * 5) // 60
            minute = (row * 5) % 60
            am_pm = 'AM' if hour < 12 else 'PM'

            if hour == 0 and minute == 0:
                time_label = QTableWidgetItem('Midnight')
            elif hour == 0 and minute != 0:
                time_label = QTableWidgetItem(f'{12}:{minute:02d} {am_pm}')
            elif hour == 12 and minute == 0:
                time_label = QTableWidgetItem('Noon')
            else:
                hour = hour % 12
                if hour == 0:
                    hour = 12
                time_label = QTableWidgetItem(f'{hour}:{minute:02d} {am_pm}')

            self.table.setVerticalHeaderItem(row, time_label)

        # Set the horizontal header labels (days of the week)
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for col, day in enumerate(days_of_week):
            day_label = QTableWidgetItem(day)
            self.table.setHorizontalHeaderItem(col, day_label)

        # Configure table properties
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide horizontal scroll bar

        self.layout.addWidget(self.table)

    def create_toggleBlock_button(self):
        self.toggleBlock_button = QCheckBox("Toggle Website Blocking")
        self.toggleBlock_button.toggled.connect(self.websiteBlocking)
        self.layout.addWidget(self.toggleBlock_button)

    def create_auto_scheduler_button(self):
        self.auto_scheduler_button = QPushButton("Create Schedule")
        self.auto_scheduler_button.clicked.connect(self.show_add_schedule_dialog)
        self.layout.addWidget(self.auto_scheduler_button)

    def create_add_event_button(self):
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self.show_add_event_dialog)
        self.layout.addWidget(self.add_event_button)

    def show_add_schedule_dialog(self):
        dialog = AddScheduleDialog()
        dialog.schedule_created.connect(self.add_schedule)
        dialog.exec()

    def show_add_event_dialog(self):
        dialog = AddEventDialog()
        dialog.event_created.connect(self.add_event)
        dialog.exec()

    def websiteBlocking(self):
        websiteBlocker = WebsiteBlocking()
        if self.toggleBlock_button.isChecked() or self.check_current_event() == True:
            websiteBlocker.activeBlocking()

        else:
            websiteBlocker.inactiveBlocking()

    def add_schedule(self, schedule):
        # Create an empty list to store the scheduled tasks
        scheduled_tasks = []

        # Iterate through the list of tasks and add their information to the prompt
        for i, task in enumerate(schedule):
            # Initialize the prompt with the information from previous tasks
            prompt = "Given the following tasks, schedule the events, use same date format at 'Due Date' variable:\n"

            prompt += f"{i + 1}. Task: {task['title']}\n"
            prompt += f"   Description: {task['description']}\n"
            prompt += f"   Duration: {task['duration']} minutes\n"
            prompt += f"   Due Date: {task['duedate'].toString()}\n"
            prompt += f"   Start Time: [start time]\n"
            prompt += f"   End Time: [end time]\n\n"

            # Make an API call to GPT-3.5 to generate the start and end times
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,  # Adjust the max tokens as needed
                n=1,  # Specify the number of responses you want
                stop=None,  # You can customize the stopping condition if needed
            )

            # Extract the generated start and end times from the API response
            # Extract the start time
            start_datetime = response.choices[0].text.split("Start Time: ")[1].split("\n")[0]

            # Extract the end time
            end_datetime = response.choices[0].text.split("End Time: ")[1].split("\n")[0]

            start_datetime = datetime.strptime(start_datetime, "%a %b %d %H:%M:%S %Y")
            end_datetime = datetime.strptime(end_datetime, "%a %b %d %H:%M:%S %Y")
            # DEBUG
            print("Start Datetime:", start_datetime)
            print("End Datetime:", end_datetime)

            scheduled_task = {
                'title': task['title'],
                'description': task['description'],
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'color': task['color']
            }
            scheduled_tasks.append(scheduled_task)

        # Print the scheduled tasks
        for task in scheduled_tasks:
            self.add_event(task)

        # Append the scheduled tasks to the events list
        self.events.extend(scheduled_tasks)

        print(self.events)

    def add_event(self, event):
        start_datetime = event['start_datetime']
        end_datetime = event['end_datetime']

        start_datetime = start_datetime.toPython()
        end_datetime = end_datetime.toPython()

        start_row = self.time_to_row(start_datetime.time())
        end_row = self.time_to_row(end_datetime.time())

        for row in range(start_row, end_row + 1):
            for col in range(start_datetime.date().weekday() % 7, (end_datetime.date().weekday() + 1) % 7):
                existing_item = self.table.item(row, col)
                if existing_item:
                    existing_event = existing_item.data(Qt.UserRole)
                    QMessageBox.warning(self, "Conflict",
                                        f"There is already an event scheduled at this time: {existing_event['title']}")
                    return

                event_item = QTableWidgetItem(event['title'])
                event_item.setData(Qt.UserRole, event)
                if event['color']:
                    brush = QBrush(event['color'])
                    event_item.setBackground(brush)
                self.table.setItem(row, col, event_item)

    def time_to_row(self, time):
        hour = time.hour
        minute = time.minute

        row = ((hour * 60 + minute) // 5)
        return row

    def start_timer(self):
        # Create a QTimer object
        self.timer = QTimer()

        # Connect the timeout signal to the check_current_event() method
        self.timer.timeout.connect(self.check_current_event)

        # Set the interval to 1 minute (60,000 milliseconds)
        interval = 30_000

        # Start the timer with the specified interval
        self.timer.start(interval)

    def check_current_event(self):
        current_time = QTime.currentTime()

        # Get the row corresponding to the current time
        current_time = current_time.toPython()
        current_row = self.time_to_row(current_time)

        # Get the column corresponding to the current day
        current_day = datetime.now().weekday() % 7

        # Check if there is an event at the current time and day
        item = self.table.item(current_row, current_day)
        if item:
            print("Current Event!!")
            return True
        else:
            print("No event")
            return False


class AddScheduleDialog(QDialog):
    schedule_created = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Schedule")

        layout = QFormLayout()
        self.setLayout(layout)

        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)

        self.description_input = QLineEdit()
        layout.addRow("Description:", self.description_input)

        self.duration_input = QLineEdit()
        layout.addRow("Duration:", self.duration_input)

        self.duedate_input = QDateTimeEdit()
        self.duedate_input.setCalendarPopup(True)
        layout.addRow("Due Date:", self.duedate_input)

        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        layout.addRow("Color:", self.color_button)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_schedule)
        layout.addRow(self.add_button)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_schedule)
        layout.addRow(self.submit_button)

        self.selected_color = None

        # Initialize a list to store the created schedules
        self.schedule_list = []

    def select_color(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.selected_color = color

    def add_schedule(self):
        title = self.title_input.text()
        description = self.description_input.text()
        duration = self.duration_input.text()
        duedate = self.duedate_input.dateTime()

        task = {
            'title': title,
            'description': description,
            'duration': duration,
            'duedate': duedate,
            'color': self.selected_color
        }

        # Append the schedule to the list
        self.schedule_list.append(task)

        # Clear the input fields for the next schedule
        self.clear_inputs()

    def submit_schedule(self):
        # self.add_schedule()

        # Emit the signal with the list of schedules
        self.schedule_created.emit(self.schedule_list)
        self.accept()
        print(self.schedule_list)

    def clear_inputs(self):
        self.title_input.clear()
        self.description_input.clear()
        self.duration_input.clear()
        self.duedate_input.clear()
        self.selected_color = None


class AddEventDialog(QDialog):
    event_created = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Event")

        layout = QFormLayout()
        self.setLayout(layout)

        self.title_input = QLineEdit()
        layout.addRow("Title:", self.title_input)

        self.description_input = QLineEdit()
        layout.addRow("Description:", self.description_input)

        self.start_datetime_input = QDateTimeEdit()
        self.start_datetime_input.setCalendarPopup(True)
        layout.addRow("Start DateTime:", self.start_datetime_input)

        self.end_datetime_input = QDateTimeEdit()
        self.end_datetime_input.setCalendarPopup(True)
        layout.addRow("End DateTime:", self.end_datetime_input)

        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        layout.addRow("Color:", self.color_button)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.create_event)
        layout.addRow(self.ok_button)

        self.selected_color = None

    def select_color(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.selected_color = color

    def create_event(self):
        title = self.title_input.text()
        description = self.description_input.text()
        start_datetime = self.start_datetime_input.dateTime()
        end_datetime = self.end_datetime_input.dateTime()

        event = {
            'title': title,
            'description': description,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'color': self.selected_color
        }

        self.event_created.emit(event)
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ScheduleWidget()
    widget.show()
    sys.exit(app.exec())
