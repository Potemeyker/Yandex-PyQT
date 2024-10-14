import sys
import sqlite3

from random import choice

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap


class MainWindow(QMainWindow):
    """������� ���� � ��������� �����������, ��� ������������ �������� ��� �����,
                                                              ��������� ��,
                                                              ��������� ���� ����� � ��������� ��"""
    # ������������� ������ �������� ����
    def __init__(self):
        super().__init__()

        # �������� ���� �������� ����
        uic.loadUi("ui/main.ui", self)

        # ����������������� ����
        self.setWindowTitle("������� ����")

        # ������ ������ ������ ������� ������������ �� ������
        self.errorLabel.setAlignment(Qt.AlignCenter)

        # ���������� ���� ���
        self.pixmap = QPixmap('pictures/ege.jpg')
        self.image = QLabel(self)
        self.image.move(50, 300)
        self.image.resize(100, 80)
        self.image.setPixmap(self.pixmap)

        # ���������� �������� "������� ����"
        self.pixmap = QPixmap('pictures/ru_lang.jpg')
        self.image = QLabel(self)
        self.image.move(450, 300)
        self.image.resize(100, 80)
        self.image.setPixmap(self.pixmap)

        # ���������� ��������� �������������� ��
        with open("data/last_db.txt", "r") as file:
            self.db_name = file.readline()

        # ����� ������� ���������� ������ ����� �������
        self.update_tasks()

        # � ������ ������ ������� �������, ������� ���������� ��� �� �������
        self.loadButton.clicked.connect(self.load_data)  # ������ �������� ��
        self.changeButton.clicked.connect(self.open_change)  # ������ �������� ���� ��� ��������� ��
        self.startButton.clicked.connect(self.open_task)  # ������ �������� ���� �����

    def update_tasks(self):
        """��������� ������ taskBox (QComboBox) ������� ����� �� ������� types ���� ������, �� �������� ������������
                                                                                          �������� ��� �������� �����"""

        # ���� �� ����� ���������� ������ (�� ���������� ����������), �� ������ taskBox �����������
        try:
            # ����������� ��
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()

            # ��������� ���� ����� �� ������� types
            tasks = map(lambda x: f'{x[0]}. {x[1]}', cur.execute("SELECT * FROM types").fetchall())

            # ���������� ������ � taskBox
            self.taskBox.addItems(tasks)

            # ����� ������������ ��������� �� �������� �������� ��
            self.errorLabel.setText("���� ������ ������� ���������")

            # ����������� � ���� ��������� �������������� ��
            with open("data/last_db.txt", "w") as file:
                file.write(self.db_name)

        # ��� ������ ���������� ������ taskBox ��������� � ������ ��������� ������������
        except sqlite3.OperationalError or sqlite3.DatabaseError:
            # �������� ������
            self.taskBox.clear()
            # ����� ������
            self.errorLabel.setText("��������� ���������� ��� ������ ���� ������")

    def load_data(self):
        """��������� ���� ���� ������ ����� ���������� ����"""

        # �������� ������������� ����� ��
        self.db_name = QFileDialog.getOpenFileName(self, "������� ���� ������", '',
                                                   "���� ������ (*.sqlite);;��� ����� (*)")[0]

        # ����� ������� ���������� ������ ����� �������
        self.update_tasks()

    def open_change(self):
        """��������� ���� ��� ��������� ������� tasks �� ��"""

        # ���� ��������� �� ������� �������, �� ���� �����������
        if self.errorLabel.text() == "���� ������ ������� ���������":
            # �������� ����
            self.change = ChangeWidget()
            self.change.show()

            # �������� �������� ����
            self.hide()

    def open_task(self):
        """��������� ���� �����"""

        # ���� ��� ������� �� ������, �� ������������ ��������� ������
        if self.errorLabel.text() == "���� ������ ������� ���������" and self.taskBox.currentText() == "":
            self.errorLabel.setText("�������� ��� ����� ��� �������")
        # ���� ��������� �� ������� �������, �� ���� ����� �����������
        else:
            # �������� ���� (������ ��������� ��������� ��� �������)
            self.task = TaskWidget(self.taskBox.currentText().split('. ')[0])
            self.task.show()

            # �������� �������� ����
            self.hide()


class TaskWidget(QWidget):
    """����� ���� �����, ��� ������������ ������ ������ ���������� � ������� ���� ���� �����"""

    # ������������� ������ ���� ����� � �������� ��������� ����
    def __init__(self, type_tasks):
        super().__init__()

        # �������� ����
        uic.loadUi("ui/task.ui", self)

        # ���������������� ����
        self.setWindowTitle("����")

        # �������� ��������� ���� �������
        self.type_task = type_tasks

        # �������� ���������� ���������� (������ ����� - ���. ��������� �������� �������, ������ - ����� ���. �����)
        self.stat = [0, 0]

        # ���������� ��� �� �� ����� ��������� �������������� ��
        with open("data/last_db.txt", "r") as file:
            self.db_name = file.readline()

        # ����������� ��
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        # �������� �� ������� tasks ������� � ����������� �����
        self.data = self.cur.execute(f"SELECT title, body, answer FROM tasks WHERE type = {self.type_task}").fetchall()

        # ����� ������� ������ ������������ ������ �������
        self.new_task()

        # ������ ������ ���������� ������� ������������ �� ������
        self.statText.setAlignment(Qt.AlignCenter)

        # � ������ ������ ������� �������, ������� ���������� ��� �� �������
        self.backButton.clicked.connect(self.close_widget)  # ������ ���������� �����
        self.showButton.clicked.connect(self.show_ans)  # ������ ������ ������ �� �������
        self.checkButton.clicked.connect(self.check_ans)  # ������ �������� ��������� ������
        self.nextButton.clicked.connect(self.new_task)  # ������ �������� � ���������� �������

    def update_stat(self):
        """������� ���������� ���������� ������������"""

        # ����� ����������
        self.statText.setText(f'{self.stat[0]} �� {self.stat[1]}\n����������')
        # ������� ������ ������������ �� ������
        self.statText.setAlignment(Qt.AlignCenter)

    def new_task(self):
        """������� ��������� ��������� ������� ������������"""

        # ����� ���������� ������� � ����������� ��� ������ � ��������������� ����������
        self.title, self.body, self.answer = choice(self.data)

        # ����� ������������ ������ � ����� �������
        self.titleText.setText(self.title)
        self.bodyText.setText(self.body)

        # �������� ���� ������ ������
        self.ansLabel.setText(f'�����: ')
        self.answerEdit.setText(f'')

        # �������� ��������� ��� �������� ������ �� �������
        self.task_done = False

    def show_ans(self):
        """������� ������������ ����� �� �������"""

        # ����� ������
        self.ansLabel.setText(f'�����: {self.answer}')

        # ���� ������� ��� �� ������, �� ����� ���. �������� ������� �������������
        if not self.task_done:
            # ���������� ����� ���. �������� �������
            self.stat[1] += 1

            # ������� ������
            self.task_done = True

            # ����� ������� ���������� ����������
            self.update_stat()

    def check_ans(self):
        """��������� ������ �� ��������� �������"""

        # ���� ������� ��� �� ������, �� ���. ��������� �������� ������� �������������
        if not self.task_done:

            # ���� �������� ������������� ����� ����� �����������, �� ���. ��������� �������� ������� �������������
            if self.answerEdit.text() == self.answer:
                self.stat[0] += 1

            # ����� ������� ������ ��������� ������
            self.show_ans()

            # ����� ������� ���������� ����������
            self.update_stat()

    def close_widget(self):
        """��������� ���� ����� � ��������� ������� ����"""
        self.close()
        ex.show()


class ChangeWidget(QWidget):
    """����� ��� ���� ��������� ������� � ��������� (tasks) �� ��"""

    # ������������� ������ ���� ��� ��������� ��
    def __init__(self):
        super().__init__()

        # �������� ����
        uic.loadUi('ui/change.ui', self)

        # ���������������� ����
        self.setWindowTitle("�������� ��")

        # ���������� ��� �� �� ����� ��������� �������������� ��
        with open("data/last_db.txt", "r") as file:
            self.db_name = file.readline()

        # ����������� ��
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        # ����������� �� ����� PyQT ��� ������ ������
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.db_name)
        self.db.open()

        # ����� ������� ������ ������
        self.load_table()

        # � ������ ������ ������� �������, ������� ���������� ��� �� �������
        self.backButton.clicked.connect(self.close_check)  # ������ ���������� �����
        self.addButton.clicked.connect(self.add)  # ������ ���������� �������
        self.changeButton.clicked.connect(self.change)  # ������ ��������� ������� �� id
        self.deleteButton.clicked.connect(self.delete)  # ������ �������� ������� �� id

    def add(self):
        """��������� ������� � ��������� ������"""

        # ���������� �������� ������
        type_ = self.typeAdd.toPlainText()
        title = self.titleAdd.toPlainText()
        body = self.bodyAdd.toPlainText()
        answer = self.ansAdd.toPlainText()

        # ��������� ���� ����� �������
        types = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM types""")))

        # ���� ��������� ���� ������� �� ����������, �� ��������� ��������������� ������
        if type_ not in types:
            self.message.setText("��������� ���� ������� �� ����������")
        # ���� ���� �� ���� �� �������� ������ ������, �� ��������� �������������� ������
        elif title == "":
            self.message.setText("������ ������� �� ����� ���� ������")
        elif body == "":
            self.message.setText("����� ������� �� ����� ���� ������")
        elif answer == "":
            self.message.setText("����� �� ����� ���� ������")
        # ����� ������� �����������
        else:
            # ���������� �������
            self.cur.execute(f"""INSERT INTO tasks (type, title, body, answer) 
                                 VALUES ({type_}, '{title}', '{body}', '{answer}')""")

            # ���������� ��
            self.con.commit()

            # ����� ������� �������� ������
            self.load_table()

            # ����� ������������ ��������� �� �������� ����������
            self.message.setText("������� ������� ���������")

    def change(self):
        """�������� �� id ������ ������� �� ��������"""

        # ���������� �������� ������
        id_ = self.idChange.toPlainText()
        type_ = self.typeChange.toPlainText()
        title = self.titleChange.toPlainText()
        body = self.bodyChange.toPlainText()
        answer = self.ansChange.toPlainText()

        # ��������� ���� ����� �������
        types = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM types""")))
        # ��������� ���� id �������
        ids = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM tasks""")))

        # ���� ��������� ���� ��� id ������� �� ����������, �� ��������� ��������������� ������
        if type_ not in types:
            self.message.setText("��������� ���� ������� �� ����������")
        elif id_ not in ids:
            self.message.setText("��������� id �� ����������")
        # ���� ���� �� ���� �� �������� ������ ������, �� ��������� �������������� ������
        elif title == "":
            self.message.setText("������ ������� �� ����� ���� ������")
        elif body == "":
            self.message.setText("����� ������� �� ����� ���� ������")
        elif answer == "":
            self.message.setText("����� �� ����� ���� ������")
        # ����� ������ ������� ����������
        else:
            # ��������� ������
            self.cur.execute(f"""UPDATE tasks SET type = {type_} WHERE id = {id_}""")
            self.cur.execute(f"""UPDATE tasks SET title = '{title}' WHERE id = {id_}""")
            self.cur.execute(f"""UPDATE tasks SET body = '{body}' WHERE id = {id_}""")
            self.cur.execute(f"""UPDATE tasks SET answer = '{answer}' WHERE id = {id_}""")

            # ���������� ��
            self.con.commit()

            # ����� ������� �������� ������
            self.load_table()

            # ����� ������������ ��������� �� �������� ���������
            self.message.setText("������� ������� ��������")

    def delete(self):
        """�������� ������� �� id"""

        # ���������� ��������� id
        id_ = self.idDelete.toPlainText()

        # ��������� ���� id �������
        ids = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM tasks""")))

        # ���� ��������� id ������� �� ����������, �� ��������� ��������������� ������
        if id_ not in ids:
            self.message.setText("��������� id �� ����������")
        # ����� ������� ���������
        else:
            # �������� �������
            self.cur.execute(f"""DELETE FROM tasks WHERE id = {id_}""")

            # ���������� ��
            self.con.commit()

            # ����� ������� �������� ������
            self.load_table()

            # ����� ������������ ��������� �� �������� ��������
            self.message.setText("������� ������� �������")

    def load_table(self):
        """������� ������������ 2 ������� ��: ������� (tasks) � ���� ������� (types)"""

        # ����� ������� �������
        tasks = QSqlTableModel(self, self.db)
        tasks.setTable('tasks')
        tasks.select()
        self.taskTable.setModel(tasks)
        self.taskTable.show()

        # ����� ������� ����� �������
        types = QSqlTableModel(self, self.db)
        types.setTable('types')
        types.select()
        self.typeTable.setModel(types)
        self.typeTable.show()

    def close_check(self):
        """��������� ���� � ��������� ������� ����"""

        # ���������� ��
        self.con.commit()
        self.con.close()
        # �������� ����
        self.close()
        # �������� �������� ����
        ex.show()


def except_hook(cls, exception, traceback):
    """������� ������ � ����������"""
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
