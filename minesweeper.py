import random
import math
import sys
import pygame

class Button:
    def __init__(self, y, x, size, what_in, i, j, surface=0, surrounding=0):
        self.x = x
        self.y = y
        self.size = size
        self.condition = 'close'
        self.what_in = what_in
        self.i = i
        self.j = j
        self.surface = surface
        self.surrounding = surrounding
    def is_cursor_in(self, x_cursor, y_cursor):
        if self.x - self.size < x_cursor < self.x + self.size and self.y - self.size < y_cursor < self.y + self.size:
            return True
        else:
            return False
    def surround(self, button, cell_x, cell_y):
        sur = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= self.i + dy < cell_y and 0 <= self.j + dx < cell_x:
                    if button[hash(cell_x, self.i + dy, self.j + dx)].surface == -1:
                        sur += 1
        if self.surface == -1:
            sur -= 1
        self.surrounding = sur

cell_x = 30
cell_y = 16
number_mines = 99
size = 20
def hash(cell_x, y, x):
    return y * cell_x + x

def back_hash(hash, cell_y, cell_x):
    true = [0] * 2

    for y in range(cell_y):
        if y*cell_x <= hash <= (y+1) * cell_x - 1:
            true[0] = y
            break

    true[1] = hash - true[0] * cell_x

    return true

def set_mines(cell_y, cell_x, restr_y, restr_x, number_mines):
    restr_hash = hash(cell_x, restr_y, restr_x)
    pull = [i for i in range(cell_x * cell_y)]
    pull.pop(restr_hash)
    set_hash = [0] * number_mines

    for i in range(number_mines):
        hash_tmp_index = random.randint(0, len(pull) - 1)
        set_hash[i] = pull[hash_tmp_index]
        pull.pop(hash_tmp_index)

    set_mines = [[0] * 2 for i in range(number_mines)]

    for i in range(number_mines):
        set_mines[i] = back_hash(set_hash[i], cell_y, cell_x)

    return set_mines

def set_field(cell_y, cell_x, set_mines):
    field = [[0] * cell_x for i in range(cell_y)]

    for i in range(len(set_mines)):
        field[set_mines[i][0]][set_mines[i][1]] = -1

    for i in range(cell_y):
        for j in range(cell_x):
            if field[i][j] >= 0:
                for dx in (-1, 0, +1):
                    for dy in (-1, 0, +1):
                        if 0 <= i + dy < cell_y and 0 <= j + dx < cell_x:
                            if field[i + dy][j + dx] == -1:
                                field[i][j] += 1

    return field

def open_cell(y, x, field, cell_y, cell_x):
    open = []
    there_is_zeros = True
    cash_index = []
    index = [[y, x]]
    while there_is_zeros:
        there_is_zeros = False
        for i in range(len(index)):
            if index[i] not in cash_index:
                cash_index.append(index[i])
                for dx in (-1, 0, +1):
                    for dy in (-1, 0, +1):
                        if 0 <= index[i][0] + dy < cell_y and 0 <= index[i][1] + dx < cell_x:
                            if field[index[i][0] + dy][index[i][1] + dx] == 0:
                                open.append([index[i][0] + dy, index[i][1] + dx])
                                there_is_zeros = True
                                index.append([index[i][0] + dy, index[i][1] + dx])
    open_final = []
    beg = 0
    if field[y][x] == 0:
        beg = 1
    for i in range(beg, len(open)):
        for dx in (-1, 0, +1):
            for dy in (-1, 0, +1):
                if 0 <= open[i][0] + dy < cell_y and 0 <= open[i][1] + dx < cell_x:
                    open_final.append([open[i][0] + dy, open[i][1] + dx])
    open_final.append([y, x])
    return open_final

def find_button(button, x_cursor, y_cursor):
    for i in range(len(button)):
        if Button.is_cursor_in(button[i], x_cursor, y_cursor):
            return i

button = []
for i in range(cell_y):
    for j in range(cell_x):
        button.append(Button(i * 2 * size + size, j * 2 * size + size, size, 0, i, j))

pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 20)
screen = pygame.display.set_mode((cell_x * 2 * size, cell_y * 2 * size))


game_over = False
first_touch = False
flag = True
screen.fill((133, 133, 133))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            flag = True

    if flag and first_touch is False and pygame.mouse.get_pressed()[0]:
        flag = False
        first_touch = True

        x_cursor, y_cursor = pygame.mouse.get_pos()
        restr_x, restr_y = x_cursor, y_cursor
        index = find_button(button, x_cursor, y_cursor)
        mines = set_mines(cell_y, cell_x, button[index].i, button[index].j, number_mines)
        field = set_field(cell_y, cell_x, mines)

        for i in range(cell_y):
            for j in range(cell_x):
                button[hash(cell_x, i, j)].what_in = field[i][j]

        open = open_cell(button[index].i, button[index].j, field, cell_y, cell_x)
        for i in range(len(open)):
            button[hash(cell_x, open[i][0], open[i][1])].condition = 'open'

    if flag and first_touch and pygame.mouse.get_pressed()[0]:
        flag = False
        x_cursor, y_cursor = pygame.mouse.get_pos()
        index = find_button(button, x_cursor, y_cursor)
        if button[index].what_in == -1:
            game_over = True
        open = open_cell(button[index].i, button[index].j, field, cell_y, cell_x)
        for i in range(len(open)):
            button[hash(cell_x, open[i][0], open[i][1])].condition = 'open'

        Button.surround(button[index], button, cell_x, cell_y)
        if button[index].condition == 'open' and button[index].what_in == button[index].surrounding:
            for dx in (-1, 0, +1):
                for dy in (-1, 0, +1):
                    if 0 <= button[index].i + dy < cell_y and 0 <= button[index].j + dx < cell_x:
                        if button[hash(cell_x, button[index].i + dy, button[index].j + dx)].surface != -1:
                            open = open_cell(button[index].i + dy, button[index].j + dx, field, cell_y, cell_x)
                            for i in range(len(open)):
                                button[hash(cell_x, open[i][0], open[i][1])].condition = 'open'
                                if button[hash(cell_x, open[i][0], open[i][1])].what_in == -1:
                                    game_over = True

    if flag and first_touch and pygame.mouse.get_pressed()[2]:
        flag = False
        x_cursor, y_cursor = pygame.mouse.get_pos()
        index = find_button(button, x_cursor, y_cursor)
        if button[index].surface == -1:
            button[index].surface = 0
        else:
            button[index].surface = -1

    if flag and first_touch and pygame.mouse.get_pressed()[1]:
        flag = False
        x_cursor, y_cursor = pygame.mouse.get_pos()
        index = find_button(button, x_cursor, y_cursor)
        Button.surround(button[index], button, cell_x, cell_y)
        if button[index].condition == 'open' and button[index].what_in == button[index].surrounding:
            for dx in (-1, 0, +1):
                for dy in (-1, 0, +1):
                    if 0 <= button[index].i + dy < cell_y and 0 <= button[index].j + dx < cell_x:
                        if button[hash(cell_x, button[index].i + dy, button[index].j + dx)].surface != -1:
                            open = open_cell(button[index].i + dy, button[index].j + dx, field, cell_y, cell_x)
                            for i in range(len(open)):
                                button[hash(cell_x, open[i][0], open[i][1])].condition = 'open'
                                if button[hash(cell_x, open[i][0], open[i][1])].what_in == -1:
                                    game_over = True

    for i in range(len(button)):
        pygame.draw.rect(screen, (0, 0, 0), [button[i].x - size, button[i].y - size, button[i].x + size, button[i].y + size], 2)
    for i in range(len(button)):
        if button[i].condition == 'open':
            pygame.draw.rect(screen, (255, 255, 255), [button[i].x - size, button[i].y - size, button[i].x + size, button[i].y + size])
            pygame.draw.rect(screen, (0, 0, 0), [button[i].x - size, button[i].y - size, button[i].x + size, button[i].y + size], 2)
            if button[i].what_in == 0:
                label = myfont.render('', 1, (0, 0, 0))
            elif button[i].what_in == -1:
                label = myfont.render('M', 1, (0, 0, 0))
            else:
                label = myfont.render(str(button[i].what_in), 1, (0, 0, 0))
            screen.blit(label, (button[i].x - size, button[i].y - size))
        else:
            pygame.draw.rect(screen, (133, 133, 133), [button[i].x - size, button[i].y - size, button[i].x + size, button[i].y + size])
            pygame.draw.rect(screen, (0, 0, 0), [button[i].x - size, button[i].y - size, button[i].x + size, button[i].y + size], 2)
            if button[i].surface == -1:
                label = myfont.render('M', 1, (255, 0, 0))
            else:
                label = myfont.render('', 1, (0, 0, 0))
            screen.blit(label, (button[i].x - size, button[i].y - size))
    if game_over:
        screen.fill((255, 0, 0))
        textsurface = myfont.render('Game Over', True, (200, 200, 0))
        screen.blit(textsurface, (cell_x * size, cell_y * size))


    pygame.display.flip()





