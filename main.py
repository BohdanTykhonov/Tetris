import tkinter as tk
import random

class Tetris(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Тетріс")

        # Встановлюємо розміри вікна
        self.window_width = Board.BoardWidth * Board.CellSize
        self.window_height = Board.BoardHeight * Board.CellSize

        # Отримуємо розміри екрану
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Обчислюємо позицію для центрування вікна
        x_position = (screen_width - self.window_width) // 2
        y_position = (screen_height - self.window_height) // 2

        # Встановлюємо положення вікна по центру
        self.geometry(f"{self.window_width}x{self.window_height}+{x_position}+{y_position}")

        # Забороняємо змінювати розміри вікна
        self.resizable(False, False)

        # Створюємо і запускаємо ігрову дошку
        self.board = Board(self)
        self.board.pack()
        self.board.start_game()  # Запуск гри

class Board(tk.Canvas):
    BoardWidth = 10  # Ширина поля в клітинках
    BoardHeight = 22  # Висота поля в клітинках
    CellSize = 30  # Розмір кожної клітинки в пікселях
    Speed = 500  # Швидкість оновлення гри у мілісекундах
    score = 0  # Лічильник балів

    # Фігури для Тетрісу
    shapes = [
        {"shape": [(0, 0), (1, 0), (0, 1), (1, 1)], "color": "yellow"},  # Квадрат
        {"shape": [(0, 1), (1, 1), (1, 0), (2, 0)], "color": "red"},  # Z-подібна
        {"shape": [(0, 0), (1, 0), (1, 1), (2, 1)], "color": "green"},  # S-подібна
        {"shape": [(0, 0), (0, 1), (0, 2), (0, 3)], "color": "cyan"},  # Лінія
        {"shape": [(1, 0), (0, 1), (1, 1), (2, 1)], "color": "purple"},  # T-подібна
        {"shape": [(0, 0), (1, 0), (2, 0), (2, 1)], "color": "orange"},  # L-подібна
        {"shape": [(0, 1), (1, 1), (2, 1), (2, 0)], "color": "blue"},  # Зворотна L-подібна
    ]

    def __init__(self, parent):
        super().__init__(parent, width=self.BoardWidth * self.CellSize, height=self.BoardHeight * self.CellSize, bg='black')
        self.parent = parent
        self.bind_all("<Key>", self.on_key_press)
        self.score_text = self.create_text(50, 10, text="Бали: 0", fill="white", font=("Arial", 16))
        self.game_over_text = None

        # Створюємо кнопку перезапуску
        self.retry_button = tk.Button(self.parent, text="Спробувати ще", font=("Arial", 14), command=self.restart_game)
        self.retry_button.place_forget()  # Ховаємо кнопку до завершення гри

        self.init_game()

    def init_game(self):
        """Ініціалізація гри"""
        self.board = [[0] * self.BoardWidth for _ in range(self.BoardHeight)]
        self.current_piece = None
        self.current_color = None
        self.game_over = False
        self.score = 0
        self.update_score()
        self.new_piece()
        self.update_board()

    def start_game(self):
        """Запуск гри"""
        self.init_game()

    def new_piece(self):
        """Створення нової фігури"""
        shape_data = random.choice(Board.shapes)
        self.current_piece = [(x + 5, y) for x, y in shape_data["shape"]]  # Початкова позиція
        self.current_color = shape_data["color"]  # Встановлюємо колір фігури
        if not self.check_position(self.current_piece):
            self.game_over = True
            self.show_game_over_text()

    def check_position(self, piece):
        """Перевірка можливості розташування фігури на полі"""
        for x, y in piece:
            if x < 0 or x >= self.BoardWidth or y >= self.BoardHeight or (y >= 0 and self.board[y][x]):
                return False
        return True

    def on_key_press(self, event):
        """Обробка натискання клавіш"""
        if self.game_over:
            return
        if event.keysym == "Left":
            self.move_piece((-1, 0))
        elif event.keysym == "Right":
            self.move_piece((1, 0))
        elif event.keysym == "Down":
            self.move_piece((0, 1))
        elif event.keysym == "Up":
            self.rotate_piece()

    def move_piece(self, direction):
        """Переміщення фігури в заданому напрямку"""
        new_position = [(x + direction[0], y + direction[1]) for x, y in self.current_piece]
        if self.check_position(new_position):
            self.current_piece = new_position
        else:
            if direction == (0, 1):  # Якщо фігура не може рухатися вниз
                self.freeze_piece()
                self.remove_full_lines()
                self.new_piece()
        self.draw_board()

    def rotate_piece(self):
        """Поворот фігури"""
        x_center, y_center = self.current_piece[0]
        rotated_piece = [(x_center + y - y_center, y_center - x + x_center) for x, y in self.current_piece]

        # Якщо фігура виходить за межі або накладається, скасовуємо поворот
        if self.check_position(rotated_piece):
            self.current_piece = rotated_piece
        else:
            # Спробуємо змістити фігуру ліворуч або праворуч для коректного повороту
            for shift in [-1, 1]:  # Зсув на одну клітинку ліворуч або праворуч
                shifted_piece = [(x + shift, y) for x, y in rotated_piece]
                if self.check_position(shifted_piece):
                    self.current_piece = shifted_piece
                    break

        self.draw_board()

    def freeze_piece(self):
        """Закріплення фігури на полі"""
        for x, y in self.current_piece:
            if y >= 0:
                self.board[y][x] = 1

    def remove_full_lines(self):
        """Видалення повних ліній"""
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_removed = self.BoardHeight - len(new_board)
        self.score += lines_removed * 10  # Додаємо бали за кожну повну лінію
        self.update_score()
        while len(new_board) < self.BoardHeight:
            new_board.insert(0, [0] * self.BoardWidth)
        self.board = new_board

    def update_score(self):
        """Оновлення відображення балів"""
        self.itemconfig(self.score_text, text=f"Бали: {self.score}")

    def draw_board(self):
        """Малювання поточного стану поля та фігури"""
        self.delete("all")
        self.create_text(50, 10, text=f"Бали: {self.score}", fill="white", font=("Arial", 16))
        for y in range(self.BoardHeight):
            for x in range(self.BoardWidth):
                if self.board[y][x]:
                    self.draw_cell(x, y, "grey")  # Сірий колір для закріплених блоків
        for x, y in self.current_piece:
            self.draw_cell(x, y, self.current_color)  # Використовуємо колір поточної фігури

        if self.game_over:
            self.show_game_over_text()

    def draw_cell(self, x, y, color="blue"):
        """Малювання однієї клітинки фігури"""
        if y >= 0:
            x0 = x * self.CellSize
            y0 = y * self.CellSize
            self.create_rectangle(x0, y0, x0 + self.CellSize, y0 + self.CellSize, fill=color, outline="black")

    def show_game_over_text(self):
        """Відображення тексту про завершення гри з розмиттям фону, обведенням тексту та кнопкою перезапуску"""
        # Полупрозорий фон
        self.create_rectangle(0, 0, self.BoardWidth * self.CellSize, self.BoardHeight * self.CellSize,
                              fill="black", stipple="gray50")  # Напівпрозорий чорний фон

        # Текст завершення гри з білою обводкою
        score_text = f"Гру завершено\n\tБали: {self.score}"

        # Обвідка білим кольором
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:  # Зміщення для обвідки
            self.create_text(
                self.BoardWidth * self.CellSize // 2 + dx,
                self.BoardHeight * self.CellSize // 2 + dy,
                text=score_text, fill="white", font=("Arial", 24)
            )

        # Основний текст червоного кольору
        self.create_text(
            self.BoardWidth * self.CellSize // 2,
            self.BoardHeight * self.CellSize // 2,
            text=score_text, fill="red", font=("Arial", 24)
        )

        # Відображаємо кнопку перезапуску
        self.retry_button.place(x=self.BoardWidth * self.CellSize // 2 - 60,
                                y=self.BoardHeight * self.CellSize // 2 + 60)

    def restart_game(self):
        """Перезапуск гри"""
        self.game_over = False

        # Ховаємо кнопку перезапуску
        self.retry_button.place_forget()

        # Очищаємо поле та запускаємо гру заново
        self.delete("all")
        self.init_game()

    def update_board(self):
        """Оновлення гри"""
        if self.game_over:
            self.show_game_over_text()  # Відображаємо текст завершення гри
            return
        self.move_piece((0, 1))  # Переміщення фігури вниз
        self.after(self.Speed, self.update_board)

if __name__ == "__main__":
    app = Tetris()
    app.mainloop()
