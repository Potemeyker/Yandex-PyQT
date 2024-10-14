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
    """Главное меню с небольшой инструкцией, где пользователь выбирает тип задач,
                                                              загружает БД,
                                                              запускает окно теста и изменения ДБ"""
    # Инициализация класса главного меню
    def __init__(self):
        super().__init__()

        # загрузка темы главного меню
        uic.loadUi("ui/main.ui", self)

        # переменноевывание окна
        self.setWindowTitle("Главное меню")

        # тексту вывода ошибок задаётся выравнивание по центру
        self.errorLabel.setAlignment(Qt.AlignCenter)

        # добавление лого ЕГЭ
        self.pixmap = QPixmap('pictures/ege.jpg')
        self.image = QLabel(self)
        self.image.move(50, 300)
        self.image.resize(100, 80)
        self.image.setPixmap(self.pixmap)

        # добавление картинки "Русский язык"
        self.pixmap = QPixmap('pictures/ru_lang.jpg')
        self.image = QLabel(self)
        self.image.move(450, 300)
        self.image.resize(100, 80)
        self.image.setPixmap(self.pixmap)

        # считывание последней использованной БД
        with open("data/last_db.txt", "r") as file:
            self.db_name = file.readline()

        # вызов функции обновления списка типов заданий
        self.update_tasks()

        # к каждой кнопке задаётся функция, которая вызывается при их нажатии
        self.loadButton.clicked.connect(self.load_data)  # кнопка загрузки БД
        self.changeButton.clicked.connect(self.open_change)  # кнопка открытия окно для изменения БД
        self.startButton.clicked.connect(self.open_task)  # кнопка открытия окна теста

    def update_tasks(self):
        """Обновляет список taskBox (QComboBox) данными типов из таблицы types базы данных, из которого пользователь
                                                                                          выбирает тип решаемых задач"""

        # если БД имеет подходящий формат (не вызывается исключения), то список taskBox обновляется
        try:
            # подключение БД
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()

            # получение всех типов из таблицы types
            tasks = map(lambda x: f'{x[0]}. {x[1]}', cur.execute("SELECT * FROM types").fetchall())

            # добавление данных в taskBox
            self.taskBox.addItems(tasks)

            # вывод пользователю сообщения об успешной загрузки БД
            self.errorLabel.setText("База данных успешно загружена")

            # записывание в файл последнею использованную БД
            with open("data/last_db.txt", "w") as file:
                file.write(self.db_name)

        # при вызове исключения список taskBox очищается и ошибка выводится пользователю
        except sqlite3.OperationalError or sqlite3.DatabaseError:
            # очищение списка
            self.taskBox.clear()
            # вывод ошибки
            self.errorLabel.setText("Загрузите подходящую под формат базу данных")

    def load_data(self):
        """Загружает файл базы данных через диалоговое окно"""

        # загрузка пользователем имени БД
        self.db_name = QFileDialog.getOpenFileName(self, "Выбрать базу данных", '',
                                                   "База данных (*.sqlite);;Все файлы (*)")[0]

        # вызов функции обновления списка типов заданий
        self.update_tasks()

    def open_change(self):
        """Открывает окно для изменения таблицы tasks из БД"""

        # если загружена БД верного формата, то окно открывается
        if self.errorLabel.text() == "База данных успешно загружена":
            # открытие окна
            self.change = ChangeWidget()
            self.change.show()

            # закрытие главного меню
            self.hide()

    def open_task(self):
        """Открывает окно теста"""

        # если тип заданий не выбран, то пользователю выводится ошибка
        if self.errorLabel.text() == "База данных успешно загружена" and self.taskBox.currentText() == "":
            self.errorLabel.setText("Выберите тип задач для решения")
        # если загружена БД верного формата, то окно теста открывается
        else:
            # открытие окна (классу передаётся выбранный тип заданий)
            self.task = TaskWidget(self.taskBox.currentText().split('. ')[0])
            self.task.show()

            # закрытие главного меню
            self.hide()


class TaskWidget(QWidget):
    """Класс окна теста, где пользователь решает задачи выбранного в главном меню типа задач"""

    # инициализация класса окна теста с задачами введённого типа
    def __init__(self, type_tasks):
        super().__init__()

        # загрузка темы
        uic.loadUi("ui/task.ui", self)

        # переименовывание окна
        self.setWindowTitle("Тест")

        # создание переменой типа заданий
        self.type_task = type_tasks

        # создание переменной статистики (первое число - кол. правильно решённых заданий, второе - общее кол. задач)
        self.stat = [0, 0]

        # считывание имя БД из файла последней использованной БД
        with open("data/last_db.txt", "r") as file:
            self.db_name = file.readline()

        # подключение БД
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        # загрузка из таблицы tasks заданий с определённым типом
        self.data = self.cur.execute(f"SELECT title, body, answer FROM tasks WHERE type = {self.type_task}").fetchall()

        # вызов функции вывода пользователю нового задания
        self.new_task()

        # тексту вывода статистики задаётся выравнивание по центру
        self.statText.setAlignment(Qt.AlignCenter)

        # к каждой кнопке задаётся функция, которая вызывается при их нажатии
        self.backButton.clicked.connect(self.close_widget)  # кнопка возращения назад
        self.showButton.clicked.connect(self.show_ans)  # кнопка показа ответа на задание
        self.checkButton.clicked.connect(self.check_ans)  # кнопка проверка введённого ответа
        self.nextButton.clicked.connect(self.new_task)  # кнопка перехода к следующему задания

    def update_stat(self):
        """Выводит обновлённую статистику пользователю"""

        # вывод статистики
        self.statText.setText(f'{self.stat[0]} из {self.stat[1]}\nправильных')
        # задание тексту выравнивание по центру
        self.statText.setAlignment(Qt.AlignCenter)

    def new_task(self):
        """Выводит следующее случайное задание пользователю"""

        # выбор случайного задания и записывание его данных в соответствующие переменные
        self.title, self.body, self.answer = choice(self.data)

        # вывод пользователю вопрос и текст задания
        self.titleText.setText(self.title)
        self.bodyText.setText(self.body)

        # очищение поля вывода ответа
        self.ansLabel.setText(f'Ответ: ')
        self.answerEdit.setText(f'')

        # создание переменой для проверки решено ли задание
        self.task_done = False

    def show_ans(self):
        """Выводит пользователю ответ на задание"""

        # вывод ответа
        self.ansLabel.setText(f'Ответ: {self.answer}')

        # если задание ещё не решёно, то общее кол. решённых заданий увеличивается
        if not self.task_done:
            # увеличение общее кол. решённым заданий
            self.stat[1] += 1

            # задание решёно
            self.task_done = True

            # вызов функции обновления статистики
            self.update_stat()

    def check_ans(self):
        """Проверяет решено ли правильно задание"""

        # если задание ещё не решёно, то кол. правильно решённых заданий увеличивается
        if not self.task_done:

            # если введённый пользователем ответ равен правильному, то кол. правильно решённых заданий увеличивается
            if self.answerEdit.text() == self.answer:
                self.stat[0] += 1

            # вызов функции вывода правильно ответа
            self.show_ans()

            # вызов функции обновления статистики
            self.update_stat()

    def close_widget(self):
        """Закрывает окно теста и открывает главное меню"""
        self.close()
        ex.show()


class ChangeWidget(QWidget):
    """Класс для окна изменения таблицы с заданиями (tasks) из БД"""

    # инициализация класса окна для изменения БД
    def __init__(self):
        super().__init__()

        # загрузка темы
        uic.loadUi('ui/change.ui', self)

        # переименовывание окна
        self.setWindowTitle("Изменить БД")

        # считывание имя БД из файла последней использованной БД
        with open("data/last_db.txt", "r") as file:
            self.db_name = file.readline()

        # подключение БД
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        # подключение БД через PyQT для вывода таблиц
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(self.db_name)
        self.db.open()

        # вызов функции вывода таблиц
        self.load_table()

        # к каждой кнопке задаётся функция, которая вызывается при их нажатии
        self.backButton.clicked.connect(self.close_check)  # кнопка возращения назад
        self.addButton.clicked.connect(self.add)  # кнопка добавления задания
        self.changeButton.clicked.connect(self.change)  # кнопка изменения задания по id
        self.deleteButton.clicked.connect(self.delete)  # кнопка удаления задания по id

    def add(self):
        """Добавляет задание с введёнными данным"""

        # считывание введённых данных
        type_ = self.typeAdd.toPlainText()
        title = self.titleAdd.toPlainText()
        body = self.bodyAdd.toPlainText()
        answer = self.ansAdd.toPlainText()

        # получение всех типов заданий
        types = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM types""")))

        # если введённого типа задания не существует, то выводится соответствующая ошибка
        if type_ not in types:
            self.message.setText("Заданного типа задания не существует")
        # если хотя бы одно из введённых данных пустое, то выводится соответсвующая ошибка
        elif title == "":
            self.message.setText("Вопрос задания не может быть пустым")
        elif body == "":
            self.message.setText("Текст задания не может быть пустым")
        elif answer == "":
            self.message.setText("Ответ не может быть пустым")
        # иначе задание добавляется
        else:
            # добавление задания
            self.cur.execute(f"""INSERT INTO tasks (type, title, body, answer) 
                                 VALUES ({type_}, '{title}', '{body}', '{answer}')""")

            # сохранения ДБ
            self.con.commit()

            # вызов функции загрузки таблиц
            self.load_table()

            # вывод пользователю сообщение об успешном добавлении
            self.message.setText("Задание успешно добавлено")

    def change(self):
        """Изменяет по id данные задания на введённые"""

        # считывание введённых данных
        id_ = self.idChange.toPlainText()
        type_ = self.typeChange.toPlainText()
        title = self.titleChange.toPlainText()
        body = self.bodyChange.toPlainText()
        answer = self.ansChange.toPlainText()

        # получение всех типов заданий
        types = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM types""")))
        # получение всех id заданий
        ids = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM tasks""")))

        # если введённого типа или id задания не существует, то выводится соответствующая ошибка
        if type_ not in types:
            self.message.setText("Заданного типа задания не существует")
        elif id_ not in ids:
            self.message.setText("Заданного id не существует")
        # если хотя бы одно из введённых данных пустое, то выводится соответсвующая ошибка
        elif title == "":
            self.message.setText("Вопрос задания не может быть пустым")
        elif body == "":
            self.message.setText("Текст задания не может быть пустым")
        elif answer == "":
            self.message.setText("Ответ не может быть пустым")
        # иначе данные задания изменяются
        else:
            # изменение данных
            self.cur.execute(f"""UPDATE tasks SET type = {type_} WHERE id = {id_}""")
            self.cur.execute(f"""UPDATE tasks SET title = '{title}' WHERE id = {id_}""")
            self.cur.execute(f"""UPDATE tasks SET body = '{body}' WHERE id = {id_}""")
            self.cur.execute(f"""UPDATE tasks SET answer = '{answer}' WHERE id = {id_}""")

            # сохранения ДБ
            self.con.commit()

            # вызов функции загрузки таблиц
            self.load_table()

            # вывод пользователю сообщение об успешном изменении
            self.message.setText("Задание успешно изменено")

    def delete(self):
        """Удаление задания по id"""

        # считывание введённого id
        id_ = self.idDelete.toPlainText()

        # получение всех id заданий
        ids = list(map(lambda x: str(x[0]), self.cur.execute("""SELECT id FROM tasks""")))

        # если введённого id задания не существует, то выводится соответствующая ошибка
        if id_ not in ids:
            self.message.setText("Заданного id не существует")
        # иначе задание удаляется
        else:
            # удаление задания
            self.cur.execute(f"""DELETE FROM tasks WHERE id = {id_}""")

            # сохранения ДБ
            self.con.commit()

            # вызов функции загрузки таблиц
            self.load_table()

            # вывод пользователю сообщение об успешном удалении
            self.message.setText("Задание успешно удалено")

    def load_table(self):
        """Выводит пользователю 2 таблицы БД: задания (tasks) и типы заданий (types)"""

        # вывод таблицы заданий
        tasks = QSqlTableModel(self, self.db)
        tasks.setTable('tasks')
        tasks.select()
        self.taskTable.setModel(tasks)
        self.taskTable.show()

        # вывод таблицы типов заданий
        types = QSqlTableModel(self, self.db)
        types.setTable('types')
        types.select()
        self.typeTable.setModel(types)
        self.typeTable.show()

    def close_check(self):
        """Закрывает окно и открывает главное меню"""

        # сохранение ДБ
        self.con.commit()
        self.con.close()
        # закрытие окна
        self.close()
        # открытие главного меню
        ex.show()


def except_hook(cls, exception, traceback):
    """Выводит ошибки в компилятор"""
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
