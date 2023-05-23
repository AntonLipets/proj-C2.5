import random
class BoardOutException(Exception):
    def __str__(self):
        return "Точка за пределами поля"


class ShipsBoardedException(Exception):
    def __str__(self):
        return "Корабль не может касаться другого корабля"


class ShipBoardOutException(Exception):
    def __str__(self):
        return "Корабль имеет точку за пределами поля"


class DuplicateShotException(Exception):
    def __str__(self):
        return "Вы туда уже стреляли"

class BadBoard(Exception):
    pass

class Dot:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def __eq__(self, other):
        if self._x == other.x and self._y == other.y:
            return True
        else:
            return False

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __str__(self):
        return f'{self._x}, {self._y}'


class Ship:
    def __init__(self, x, y, length, horyzont):
        self._x = x
        self._y = y
        self._lenght = length
        self._life = length
        self._horyzont = horyzont

    def dots(self):
        dots = []
        for i in range(self._lenght):
            dots.append(Dot(self._x + i * (not self._horyzont), self._y + i * self._horyzont))
        return dots

    @property
    def life(self):
        return self._life

    @life.setter
    def life(self, value):
        self._life = value



class Board:
    def __init__(self, enemy=False):
        self._field = [["O", "O", "O", "O", "O", "O"],
                       ["O", "O", "O", "O", "O", "O"],
                       ["O", "O", "O", "O", "O", "O"],
                       ["O", "O", "O", "O", "O", "O"],
                       ["O", "O", "O", "O", "O", "O"],
                       ["O", "O", "O", "O", "O", "O"]]
        self._ships = []
        self._hid = enemy
        self._live_ship_count = 0

    def __str__(self):
        if self._hid:
            str = "Поле противника\n"
        else:
            str = "Ваше поле\n"
        str += "  | 1 | 2 | 3 | 4 | 5 | 6 |\n"
        n = 1
        for line in self._field:
            str += f'{n} '
            for cage in line:
                if cage == "\u25fc" and self._hid == True:
                    str += '| 0 '
                else:
                    str += f'| {cage} '
            str += f'|\n'
            n += 1
        return str

    def out(self, dot):
        if 0 <= dot.x < 6 and 0 <= dot.y < 6:
            return False
        else:
            return True

    def contour(self, ship):
        for dot in ship.dots():
            for i in range(3):
                for j in range(3):
                    contur_dot = Dot(dot.x + i - 1, dot.y + j -1)
                    if not (contur_dot in ship.dots() or self.out(contur_dot)):
                        self._field[contur_dot.x][contur_dot.y] = "T"

    def add_ship(self, ship):
        if any(map(self.out, ship.dots())):
            raise ShipBoardOutException()
        correct_place = True
        for dot in ship.dots():
            if not self._field[dot.x][dot.y] == "O":
                correct_place = False
        if correct_place:
            self._ships.append(ship)
            for dot in ship.dots():
                self._field[dot.x][dot.y] = "\u25fc"
        else:
            raise ShipsBoardedException()

    def shot(self, dot, auto=False):
        if self.out(dot):
            raise BoardOutException()
        if self._field[dot.x][dot.y] == "O":
            self._field[dot.x][dot.y] = "T"
            return False
        if self._field[dot.x][dot.y] == "\u25fc":
            self._field[dot.x][dot.y] = "X"
            for ship in self._ships:
                if dot in ship.dots():
                    ship.life -=1
                    if ship.life == 0:
                        self.contour(ship)
                        if not auto:
                            print("Корабль убит")
                    else:
                        if not auto:
                            print("Корабль ранен")
            return True
        raise DuplicateShotException()

    def refresh(self):
        for i in range(6):
            for j in range(6):
                if self._field[i][j] == "T":
                    self._field[i][j] = "O"

    def total_life(self):
        life = 0
        for ship in self._ships:
            life += ship.life
        return life


class Player():
    def __init__(self, self_board, enemy_board):
        self._board = self_board
        self._board_enemy = enemy_board
        self._possible_shots = []
        for x in range(6):
            for y in range(6):
                self._possible_shots.append(Dot(x, y))

    @property
    def board_enemy(self):
        return self._board_enemy

    def ask(self):
        pass

    def move(self, auto = False):
        while True:
            target = self.ask()
            try:
                hit = self._board_enemy.shot(target, auto)
            except (BoardOutException, DuplicateShotException) as err:
                if not auto:
                    print(err)
            else:
                break
        return hit


class User(Player):
    def ask(self):
        move_format = "Формат хода двузначное число. Первая цифра - строка (1-6), вторая цифра - столбец (1-6)"
        correct_move = False
        while not correct_move:
            print(self._board)
            print(self._board_enemy)
            print("Ваш ход:")
            move = input()
            if len(move) == 2:
                try:
                    x = int(move[0])
                    y = int(move[1])
                except ValueError:
                    print(move_format)
                else:
                    correct_move = True
            else:
                print(move_format)
        return Dot(x-1, y-1)


class AI(Player):
    def ask(self):
        x = random.randrange(len(self._possible_shots))
        hit = self._possible_shots[x]
        self._possible_shots.pop(x)
        return hit

class Game():
    def __init__(self):
        self.pl_board = self.random_board()
        self.ai_board = self.random_board(True)
        self.user = User(self.pl_board, self.ai_board)
        self.ai = AI(self.ai_board, self.pl_board)

    def random_board(self, enemy = False):
        correct_board = False
        while not correct_board:
            try:
                ships_len = [3, 2, 2, 1, 1, 1, 1]
                count = 1000
                board = Board(enemy)
                for tek_len in ships_len:
                    while True:
                        rotation = bool(random.getrandbits(1))
                        x = random.randrange(6)
                        y = random.randrange(6)
                        #x = random.randrange(6 - (tek_len - 1) * rotation)           работает. корабль точно поместится на поле. Но не знаю нужно ли такое в коде.
                        #y = random.randrange(6 - (tek_len - 1) * (not rotation))
                        tek_ship = Ship(x, y, tek_len, rotation)
                        try:
                            board.add_ship(tek_ship)
                        except (ShipBoardOutException, ShipsBoardedException) as err:
                            count -= 1
                            if not count:
                                raise BadBoard()
                        else:
                            board.contour(tek_ship)
                            break
            except BadBoard:
                pass
            else:
                board.refresh()
                correct_board = True
        print(board)
        return board

    def greet(self):
        print('Вас приветствует игра Морской бой\n'
              'Корабли расставляются случайно\n'
              'Формат хода двузначное число. Первая цифра - строка (1-6), вторая цифра - столбец (1-6)')

    def loop(self):
        enemy_turn = False
        game_end = False
        while not game_end:
            hit = True
            if enemy_turn:
                player = self.ai
            else:
                player = self.user
            while hit:
                hit = player.move(auto=enemy_turn)
                if hit:
                    game_end = not player.board_enemy.total_life()
                    if game_end:
                        print(player.board_enemy)
                        print("Вы проиграли") if enemy_turn else print("Вы победили")
                        break
            enemy_turn = not enemy_turn


    def start(self):
        self.greet()
        self.loop()

game = Game()
game.start()
