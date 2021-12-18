# Author: HansenH
# MIT License - Copyright (c) 2021 HansenH
# https://github.com/HansenH/Game-of-Life

import keyboard # https://github.com/boppreh/keyboard
import threading
import tkinter
import random
import copy

TABLE_COLS = 40
TABLE_ROWS = 40
TIME_INTERVAL = 0.2
NO_BORDER = True        # whether table edges are linked
WINDOW_WIDTH = 600      # UI window width
WINDOW_HEIGHT = 600     # UI window height
GRID_THICK = 2
GRID_COLOR = '#BBBBBB'
TABLE_COLOR = '#666666'
LIFE_COLOR = '#00FF00'
RANDOM_INIT_PROB = 0.25 # probability of life for randomly initialzing cells
WINDOW_ADAPT = True     # True: window can self-adapt, False: lock window size

class Main():
    '''listening key events and create gui thread'''
    def __init__(self):
        self.gui = GUI()
        self.gui.start()

        def pause(event):
            self.gui.game.pause()

        def random_init(event):
            self.gui.game.random_init()

        def cleanup(event):
            self.gui.game.cleanup()

        keyboard.on_press_key('space', pause, suppress=False)
        keyboard.on_press_key('r', random_init, suppress=False)
        keyboard.on_press_key('c', cleanup, suppress=False)


class Game(threading.Thread):
    '''game logic as a thread'''
    def __init__(self):
        super().__init__()
        self.game_over = False
        self.pausing = True
        self.table = [[0 for col in range(TABLE_COLS)] for row in range(TABLE_ROWS)] # blank table
        self.table_next = [[0 for col in range(TABLE_COLS)] for row in range(TABLE_ROWS)] # next step

    def pause(self):
        if self.pausing:
            self.calculate_next()
            self.pausing = False
        else:
            self.pausing = True

    def random_init(self):
        if self.pausing:
            for i in range(TABLE_ROWS):
                for j in range(TABLE_COLS):
                    self.table[i][j] = 1 if random.random() < RANDOM_INIT_PROB else 0

    def cleanup(self):
        if self.pausing:
            for i in range(TABLE_ROWS):
                for j in range(TABLE_COLS):
                    self.table[i][j] = 0

    def calculate_next(self):
        '''calculate the states of cells of the next step'''
        for i in range(TABLE_ROWS):
            for j in range(TABLE_COLS):
                if self.count_neighbors(i, j) == 3:  # populate
                    self.table_next[i][j] = 1
                elif self.count_neighbors(i, j) < 2:  # solitude
                    self.table_next[i][j] = 0
                elif self.count_neighbors(i, j) > 3:  # overpopulation
                    self.table_next[i][j] = 0
                else:                                 # no change
                    self.table_next[i][j] = self.table[i][j]

    def count_neighbors(self, i, j):
        '''count living neighbors around the cell (i,j)'''
        if NO_BORDER:
            return (self.table[i-1][j-1] + self.table[i-1][j] +
                    self.table[i-1][(j+1)%TABLE_COLS] + self.table[i][j-1] + 
                    self.table[i][(j+1)%TABLE_COLS] + self.table[(i+1)%TABLE_ROWS][j-1] + 
                    self.table[(i+1)%TABLE_ROWS][j] + self.table[(i+1)%TABLE_ROWS][(j+1)%TABLE_COLS])
        count = 0
        try:
            count += self.table[i-1][j-1]
            if i == 0 or j == 0: raise IndexError()
        except IndexError: pass
        try:
            count += self.table[i-1][j]
            if i == 0: raise IndexError()
        except IndexError: pass
        try:
            count += self.table[i-1][j+1]
            if i == 0: raise IndexError()
        except IndexError: pass
        try:
            count += self.table[i][j-1]
            if j == 0: raise IndexError()
        except IndexError: pass
        try:
            count += self.table[i][j+1]
        except IndexError: pass
        try:
            count += self.table[i+1][j-1]
            if j == 0: raise IndexError()
        except IndexError: pass
        try:
            count += self.table[i+1][j]
        except IndexError: pass
        try:
            count += self.table[i+1][j+1]
        except IndexError: pass
        return count


    def run(self):
        def one_step():
            if not self.game_over:
                threading.Timer(TIME_INTERVAL, one_step).start()  # create timer thread for next step
            if not self.pausing:
                for i in range(TABLE_ROWS):
                    for j in range(TABLE_COLS):
                        self.table[i][j] = self.table_next[i][j]
                self.calculate_next()
        one_step()
        

class GUI(threading.Thread):
    '''a self-adapting GUI window'''
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.game.start()

    def run(self):
        window = tkinter.Tk()
        window.withdraw()
        window.title('Game of Life')
        window_x = int((window.winfo_screenwidth() - WINDOW_WIDTH) / 2)
        window_y = int((window.winfo_screenheight() - WINDOW_HEIGHT) / 2)
        window.geometry('{}x{}+{}+{}'.format(WINDOW_WIDTH, WINDOW_HEIGHT, window_x, window_y))
        window.deiconify()

        def on_closing():
            self.game.game_over = True     # to terminate game thread
            window.destroy()
        window.protocol('WM_DELETE_WINDOW', on_closing)

        def window_adjust(event):
            '''to implement self-adapting of window'''
            canvas.configure(
                width=min(window.winfo_width(), window.winfo_height() * WINDOW_WIDTH / WINDOW_HEIGHT), 
                height=min(window.winfo_width() * WINDOW_HEIGHT / WINDOW_WIDTH, window.winfo_height()), 
            )
            draw_table(min(window.winfo_width(), window.winfo_height() * WINDOW_WIDTH / WINDOW_HEIGHT),
                    min(window.winfo_width() * WINDOW_HEIGHT / WINDOW_WIDTH, window.winfo_height()))
        
        if WINDOW_ADAPT:
            window.bind('<Configure>', window_adjust)
        else:
            window.resizable(False, False)

        canvas = tkinter.Canvas(
            window,
            highlightthickness=0,
            bd=0,
            width=WINDOW_WIDTH, 
            height=WINDOW_HEIGHT, 
            bg=GRID_COLOR
        )
        canvas.pack(expand='yes')

        cells = [[0 for col in range(TABLE_COLS)] for row in range(TABLE_ROWS)]

        def click_event(i, j):
            def switch_living_state(event):
                if self.game.pausing:
                    self.game.table[i][j] = 1 - self.game.table[i][j]
            return switch_living_state

        def draw_table(cell_width, cell_height):
            canvas.delete('all')
            for i in range(TABLE_ROWS):
                for j in range(TABLE_COLS):
                    cells[i][j] = canvas.create_rectangle(
                        j * cell_width / TABLE_COLS,
                        i * cell_height / TABLE_ROWS,
                        (j + 1) * cell_width / TABLE_COLS,
                        (i + 1) * cell_height / TABLE_ROWS,
                        fill=TABLE_COLOR, 
                        outline=GRID_COLOR, 
                        width=GRID_THICK /2,
                    )
                    canvas.tag_bind(cells[i][j], '<Button-1>', click_event(i, j))
        
        def refresh_screen():
            if not self.game.game_over:
                canvas.after(30, refresh_screen) # fps = 1000/30 = 33
                for i in range(TABLE_ROWS):
                    for j in range(TABLE_COLS):
                        if self.game.table[i][j] > 0:
                            canvas.itemconfigure(cells[i][j], fill=LIFE_COLOR)
                        else:
                            canvas.itemconfigure(cells[i][j], fill=TABLE_COLOR)

        draw_table(WINDOW_WIDTH, WINDOW_HEIGHT)
        refresh_screen()
        window.mainloop()


if __name__ == '__main__':
    main = Main()