from random import randint, randrange, choices, choice
import tkinter.ttk as ttk
from tkinter import *
from tkinter.messagebox import showerror, showinfo
from tkinter.ttk import Radiobutton
from PIL import Image, ImageGrab

from const import *


class Sudoku(Frame):
    """
    Главное окно игры "Судоку" - генератор задач разной сложности
    Наследник класса Frame библиотеки TkInter
    """
    def __init__(self):
        """ Инициализация окна программы и её виджетов """
        super().__init__()
        self.field = []  # Структура, для хранения задачи [Строка][Колонка][Число, Видимость, (^Поле, ^Метка)]
        self.number_generation = 0  # Счетчик сгенерированных полей

        # Настройки главного окна
        self.master.title('Генератор Судоку')
        self.master.iconbitmap('C:\Pythonh\ksudoku_103845.ico')
        x = self.winfo_screenwidth() // 2 - 750 // 2
        y = self.winfo_screenheight() // 2 - 480 // 2
        self.master.geometry(f'750x480+{x}+{y}')  # Размещаем игру по центру экрана
        self.master.resizable(width=False, height=False)
        self.pack(fill=BOTH, expand=1)

        # Левая панель игры
        frame2 = Frame(self, bg=COLORS['темно-пшеничный'])
        frame2.place(relheight=1, relwidth=0.57)

        self.frame = Frame(self)  # Панель игрового поля
        self.frame.place(relheight=0.76, relwidth=0.485, relx=0.04, rely=0.02)
        self.draw_lines()  # Нанесение линий игрового поля

        self.but_save = Button(frame2, text='Сохранить', cursor='heart', activebackground=COLORS['чёрный'],
                               activeforeground=COLORS['темно-пшеничный'], bg=COLORS['темно-пшеничный'],
                               font=("Georgia", 20), width=14, state=DISABLED,
                               command=self.save_to_file)
        self.but_save.pack(side=BOTTOM, pady=16)  # Кнопка "Сохранить" вызывает метод save_to_file()

        # Правая панель игры
        lbframe_right = LabelFrame(text='', bg=COLORS['пшеничный'])
        lbframe_right.place(relheight=1, relwidth=0.45, relx=0.57, rely=0)

        tl1 = Label(lbframe_right, text='Генератор Судоку', bg=COLORS['пшеничный'], font=("Georgia", 25),
                    foreground=COLORS['заголовок'])
        tl1.pack(pady=15)  # Заголовок с названием игры

        self.but_create = Button(lbframe_right, text='Создать', cursor='heart', activebackground=COLORS['чёрный'],
                                 activeforeground=COLORS['темно-пшеничный'], bg=COLORS['темно-пшеничный'],
                                 font=("Georgia", 20), width=14,
                                 command=self.fill_field)
        self.but_create.pack(side=BOTTOM, pady=16)  # Кнопка "Создать" вызывает метод fill_field()

        lbframe1 = LabelFrame(text=' Сложность: ', bg=COLORS['пшеничный'], font=("Georgia", 22))  # Область радиокнопок
        lbframe1.place(relheight=0.45, relwidth=0.4, relx=0.59, rely=0.2)
        sty = ttk.Style()
        sty.configure('Wild.TRadiobutton', background=COLORS['пшеничный'], selectcolor=COLORS['темно-пшеничный'],
                      font=("Georgia", 20))
        self.gr_level = IntVar()  # Хранит состояние нажатий радиокнопок
        rad1 = Radiobutton(lbframe1, text='Простая', cursor='heart', style='Wild.TRadiobutton',
                           variable=self.gr_level, value=1)
        rad1.pack(side=TOP, pady=6, padx=74)
        rad2 = Radiobutton(lbframe1, text='Средняя', cursor='heart', style='Wild.TRadiobutton',
                           variable=self.gr_level, value=2)
        rad2.pack(side=TOP, pady=6, padx=74)
        rad3 = Radiobutton(lbframe1, text='Сложная', cursor='heart', style='Wild.TRadiobutton',
                           variable=self.gr_level, value=3)
        rad3.pack(side=TOP, pady=6, padx=(70, 60))
        self.gr_level.set(1)

        self.show_result = BooleanVar()  # Состояние чекбокса "Показать решение", при смене - вызов change_view()
        chk1 = Checkbutton(lbframe_right, text="Показать решение", cursor='heart', bg=COLORS['пшеничный'],
                           variable=self.show_result, onvalue=1, offvalue=0, font=("Georgia", 16),
                           command=self.change_view)
        chk1.pack(side=BOTTOM)
        self.show_result.set(0)

    def change_view(self):
        """ Обновляем игровое поле при смене состояния чекбокса """
        if self.field:
            self.show_field()

    def draw_lines(self):
        """ Нанесение основных и дополнительных линий игрового поля """
        canv = Canvas(self.frame)
        canv.create_line(3, 0, 3, CANV_HEIGHT, fill=COLORS['чёрный'], width=3)
        for num in range(1, 12):
            x = CELL_SIZE * num
            if num % 3 == 0:
                canv.create_line(x, 0, x, CANV_HEIGHT, fill=COLORS['чёрный'], width=3)
            else:
                canv.create_line(x, 0, x, CANV_HEIGHT, fill=COLORS['чёрный'], width=2, dash=(4, 2))
        canv.create_line(0, 3, CANV_WIDTH, 3, fill=COLORS['чёрный'], width=3)
        for num in range(1, 12):
            y = CELL_SIZE * num
            if num % 3 == 0:
                canv.create_line(0, y, CANV_WIDTH, y, fill=COLORS['чёрный'], width=3)
            else:
                canv.create_line(0, y, CANV_WIDTH, y, fill=COLORS['чёрный'], width=2, dash=(4, 2))
        canv.pack(fill=BOTH, expand=1)

    def fill_field(self):
        """ Генерация базовой расстановки чисел и перемешивание поля """
        self.field.clear()
        self.number_generation += 1  # Увеличиваем значение счётчика
        for skip in range(ROW_COUNT):  # Заполняем 9 строк..
            line = [[(x + skip * 3 + skip // 3) % 9 + 1, True, None] for x in range(COL_COUNT)]  # .. по 9 колонок
            self.field.append(line)
        count = randint(*LEVEL[self.gr_level.get() - 1])  # Сколько ячеек будем скрывать?
        while count > 0:
            row = randint(0, 8)  # Получаем случайные координаты ячеек для скрытия
            col = randint(0, 8)
            if self.field[row][col][1]:  # Если ячейка не скрыта - скрываем (помечаем False)
                self.field[row][col][1] = False
                count -= 1
        self.super_shake()  # Вызываем метод для случайного перемешивания поля
        if self.field:  # Поле готово, разблокируем кнопку "Сохранить"
            self.but_save['state'] = NORMAL
        self.show_field()  # Отображаем задачу на игровом поле

    def show_field(self):
        """ Метод для отображения задачи на игровом поле """
        self.frame = Frame(self)
        self.frame.place(relheight=0.76, relwidth=0.485, relx=0.04, rely=0.02)
        self.draw_lines()

        for row in range(ROW_COUNT):
            for col in range(COL_COUNT):
                if self.field[row][col][1] or self.show_result.get():  # Если ячейка должна быть видна ->
                    numb_frame = LabelFrame(self.frame, borderwidth=0)  # Создаём ^Поле
                    numb_frame.place(relheight=0.08, relwidth=0.08,
                                     relx=0.02 + col * 0.11,
                                     rely=0.02 + row * 0.11)
                    if self.field[row][col][1]:  # Создаём ^Метку разную для открытой ячейки и подсказки
                        num = Label(numb_frame, text=str(self.field[row][col][0]),
                                    font=("Arial", 25), foreground=COLORS['открытые'])
                        num.pack()
                    else:
                        num = Label(numb_frame, text=str(self.field[row][col][0]),
                                    font=("Arial", 22, "italic"), foreground=COLORS['решение'])
                        num.pack()

                    self.field[row][col][2] = (numb_frame, num)  # Сохраняем кортеж (^Поле, ^Метка) в структуре

    def super_shake(self):
        """ Перемешиваем игровое поле случайными методами SHAKE_COUNT раз """
        for _ in range(SHAKE_COUNT):
            self.field = choice([self.shake1, self.shake2, self.shake3])()

    def shake1(self):
        """ Меняем строки и колонки местами """
        new_field = []
        for i in range(ROW_COUNT):
            line = []
            for j in range(COL_COUNT):
                line.append(self.field[j][i])
            new_field.append(line)
        return new_field

    def shake2(self):
        """ Меняем местами случайные две строки или колонки в пределах "троек" """
        new_fld = self.field.copy()  # Создаём копию игрового поля
        row_col = randint(0, 1)  # Выбираем, что будем менять, колонки или строки
        region = randint(0, 2)  # В пределах какой "тройки" будет перестановка
        lines = choices([0, 1, 2], k=2)  # Какие строки/колонки будут переставляться
        xrow = row_col
        xcol = (row_col + 1) % 1
        for n in range(ROW_COUNT):  # Проводим обмен значений ячеек поля
            new_fld[(n * xrow) + (region * 3 + lines[0]) * xcol][(n * xcol) + (region * 3 + lines[0]) * xrow], \
                new_fld[(n * xrow) + (region * 3 + lines[1]) * xcol][(n * xcol) + (region * 3 + lines[1]) * xrow] = \
                new_fld[(n * xrow) + (region * 3 + lines[1]) * xcol][(n * xcol) + (region * 3 + lines[1]) * xrow], \
                new_fld[(n * xrow) + (region * 3 + lines[0]) * xcol][(n * xcol) + (region * 3 + lines[0]) * xrow]
        return new_fld

    def shake3(self):
        """ Меняем местами случайные колонки или строки блоками "троек" """
        new_fld = self.field.copy()  # Создаём копию игрового поля
        row_col = randint(0, 1)  # Выбираем, что будем менять, колонки или строки
        lines = choices([0, 1, 2], k=2)  # Какие "тройки" будут переставляться
        xrow = row_col
        xcol = (row_col + 1) % 1
        for n in range(ROW_COUNT):  # Проводим обмен значений ячеек поля
            for shift in range(3):
                new_fld[(n * xrow) + (shift + lines[0] * 3) * xcol][(n * xcol) + (shift + lines[1] * 3) * xrow], \
                    new_fld[(n * xrow) + (shift + lines[1] * 3) * xcol][(n * xcol) + (shift + lines[0] * 3) * xrow] = \
                    new_fld[(n * xrow) + (shift + lines[1] * 3) * xcol][(n * xcol) + (shift + lines[0] * 3) * xrow], \
                    new_fld[(n * xrow) + (shift + lines[0] * 3) * xcol][(n * xcol) + (shift + lines[1] * 3) * xrow]
        return new_fld

    def save_to_file(self):
        """ Сохраняем текущую задачу в файл в виде картинки с номером self.number_generation """
        x = self.winfo_rootx() + self.frame.winfo_x()
        y = self.winfo_rooty() + self.frame.winfo_y()
        x1 = x + self.frame.winfo_width()
        y1 = y + self.frame.winfo_height()
        img = ImageGrab.grab().crop((x, y, x1, y1))

        try:
            img.save(f"{CONTEST_FOLDER}\\Sudoku_contest{self.number_generation:03}"
                     f"{' open' if self.show_result.get() else ''}.jpg",
                     quality="web_medium")
        except OSError as err:
            showerror(title='Не удалось сохранить файл!', message=f'{err}')
            print(f'Не удалось сохранить файл: {err}')
        finally:
            showinfo(title="Задача сохранена!", message=f"{CONTEST_FOLDER}\\Sudoku_contest{self.number_generation:03}"
                                                        f"{' open' if self.show_result.get() else ''}.jpg"
                     )
