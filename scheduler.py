from datetime import datetime


class ddCalendar:
    def __init__(self, title, description, start, end, dueDate):
        self.title = title
        self.description = description
        self.start = datetime.strptime(start, "%Y-%m-%d %H:%M")
        self.end = datetime.strptime(end, "%Y-%m-%d %H:%M")
        self.updateDuration()
        self.dueDate = dueDate

    def setDueDate(self, dueDate):
        self.dueDate = datetime.strptime(dueDate, "%Y-%m-%d %H:%M")

    def setTitle(self, title):
        self.title = title

    def setDesc(self, description):
        self.description = description

    def setStart(self, start):
        self.start = datetime.strptime(start, "%Y-%m-%d %H:%M")
        self.updateDuration()

    def setEnd(self, end):
        self.end = datetime.strptime(end, "%Y-%m-%d %H:%M")
        self.updateDuration()

    def updateDuration(self):
        self.duration = self.end - self.start

    def display(self):
        print(self.title)
        print(self.description)
        print(self.start)
        print(self.end)
        print(self.duration)
        print(self.dueDate)


eventBlock = ddCalendar("Math Homework", "pg.120-124 problems #10-34 even", "2023-05-17 09:00", "2023-05-17 11:00", "2023-05-18")
eventBlock.display()

eventBlock.setStart("2023-05-17 07:00")
eventBlock.display()
