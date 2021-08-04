import copy
from abc import *


class State(object):
    """
    Apstraktna klasa koja opisuje stanje pretrage.
    """

    @abstractmethod
    def __init__(self, board, parent=None, position=None, goal_position=None):
        """
        :param board: Board (tabla)
        :param parent: roditeljsko stanje
        :param position: pozicija stanja
        :param goal_position: pozicija krajnjeg stanja
        :return:
        """
        self.board = board
        self.parent = parent  # roditeljsko stanje
        if self.parent is None:  # ako nema roditeljsko stanje, onda je ovo inicijalno stanje
            self.position = board.find_position(self.get_agent_code())  # pronadji pocetnu poziciju
            self.goal_position = board.find_position(self.get_agent_goal_code())  # pronadji krajnju poziciju
        else:  # ako ima roditeljsko stanje, samo sacuvaj vrednosti parametara
            self.position = position
            self.goal_position = goal_position
        self.depth = parent.depth + 1 if parent is not None else 1  # povecaj dubinu/nivo pretrage

    def get_next_states(self):
        new_positions = self.get_legal_positions_medium()  # dobavi moguce (legalne) sledece pozicije iz trenutne pozicije
        next_states = []
        # napravi listu mogucih sledecih stanja na osnovu mogucih sledecih pozicija
        for new_position in new_positions:
            next_state = self.__class__(self.board, self, new_position, self.goal_position)
            next_states.append(next_state)
        return next_states

    @abstractmethod
    def get_agent_code(self):
        """
        Apstraktna metoda koja treba da vrati kod agenta na tabli.
        :return: str
        """
        pass

    @abstractmethod
    def get_agent_goal_code(self):
        """
        Apstraktna metoda koja treba da vrati kod agentovog cilja na tabli.
        :return: str
        """
        pass

    @abstractmethod
    def get_legal_positions(self):
        """
        Apstraktna metoda koja treba da vrati moguce (legalne) sledece pozicije na osnovu trenutne pozicije.
        :return: list
        """
        pass

    @abstractmethod
    def get_legal_positions_medium(self):
        """
        Apstraktna metoda koja treba da vrati moguce (legalne) sledece pozicije na osnovu trenutne pozicije.
        :return: list
        """
        pass

    @abstractmethod
    def is_final_state(self):
        """
        Apstraktna metoda koja treba da vrati da li je treuntno stanje zapravo zavrsno stanje.
        :return: bool
        """
        pass

    @abstractmethod
    def unique_hash(self):
        """
        Apstraktna metoda koja treba da vrati string koji je JEDINSTVEN za ovo stanje
        (u odnosu na ostala stanja).
        :return: str
        """
        pass
    
    @abstractmethod
    def get_cost(self):
        """
        Apstraktna metoda koja treba da vrati procenu cene
        (vrednost heuristicke funkcije) za ovo stanje.
        Koristi se za vodjene pretrage.
        :return: float
        """
        pass
    
    @abstractmethod
    def get_current_cost(self):
        """
        Apstraktna metoda koja treba da vrati stvarnu trenutnu cenu za ovo stanje.
        Koristi se za vodjene pretrage.
        :return: float
        """
        pass


class RobotState(State):
    def __init__(self, board, parent=None, position=None, goal_position=None):
        super(self.__class__, self).__init__(board, parent, position, goal_position)
        # posle pozivanja super konstruktora, mogu se dodavati "custom" stvari vezani za stanje
        # TODO 6: prosiriti stanje sa informacijom da li je robot pokupio kutiju
        self.guns = 0
        self.has_guns = False
        self.picked_guns = []
        self.sensor_area = self.find_sensor()
        self.sensor_area1 = copy.deepcopy(self.sensor_area)
        #self.sensored_positions = []
        if self.parent is not None:
            self.guns = self.parent.guns
            self.picked_guns = copy.deepcopy(self.parent.picked_guns)
            self.sensor_area = copy.deepcopy(self.parent.sensor_area)
            self.sensor_area1 = copy.deepcopy(self.parent.sensor_area1)
           #self.sensored_positions = copy.deepcopy(self.parent.sensored_positions)

    def get_agent_code(self):
        return 'r'

    def get_agent_goal_code(self):
        return 'g'

    def get_legal_positions(self):
        # d_rows (delta rows), d_cols (delta columns)
        # moguci smerovi kretanja robota (desno, levo, dole, gore)
        d_rows = []#[1, -1, 1, -1, 2, -2, 2, -2, 3, -3, 3, -3, 4, -4, 4, -4, 5, -5, 5, -5, 6, -6, 6, -6, 7, -7, 7, -7, 8,
                 # -8, 8, -8, 9, -9, 9, -9, 10, -10, 10, -10, 11, -11, 11, -11, 12, -12, 12, -12, 13, -13, 13, -13, 14, -14, 14, -14, 15, -15, 15, -15, 16, -16, 16, -16, 17, -17, 17, -17, 18,-18, 18, -18, 19, -19, 19, -19, 20, -20, 20, -20]
        d_cols = []#[1, -1, -1, 1, 2, -2, -2, 2, 3, -3, -3, 3, 4, -4, -4, 4, 5, -5, -5, 5, 6, -6, -6, 6, 7, -7, -7, 7, 8,
                  #-8, -8, 8, 9, -9, -9, 9, 10, -10, -10, 10, 11, -11, -11, 11, 12, -12, -12, 12, 13, -13, -13, 13, 14, -14, -14, 14, 15, -15, -15, 15, 16, -16, -16, 16, 17, -17, -17, 17, 18,
                  #-18, -18, 18, 19, -19, -19, 19, 20, -20, -20, 20]
        for i in range(1, 20):
            #smer1
            d_rows.append(i)
            d_cols.append(i)
            #smer2
            d_rows.append(-i)
            d_cols.append(-i)
            #smer3
            d_rows.append(-i)
            d_cols.append(i)
            #smer4
            d_rows.append(i)
            d_cols.append(-i)

        d_rows1 = [0, 0, 1, -1]
        d_cols1 = [1, -1, 0, 0]

        row, col = self.position  # trenutno pozicija
        if self.board.data[row][col] == 'b':
            if self.position not in self.picked_guns and self.guns < 2:
                self.guns += 1
                self.picked_guns.append(self.position)
        new_positions = []
        if self.guns == 2:
            for d_row, d_col in zip(d_rows1, d_cols1):  # za sve moguce smerove
                new_row = row + d_row  # nova pozicija po redu
                new_col = col + d_col  # nova pozicija po koloni
                # ako nova pozicija nije van table i ako nije zid ('w'), ubaci u listu legalnih pozicija
                if 0 <= new_row < self.board.rows and 0 <= new_col < self.board.cols and self.board.data[new_row][new_col] != 'w':
                    new_positions.append((new_row, new_col))
        else:
            for d_row, d_col in zip(d_rows, d_cols):  # za sve moguce smerove
                new_row = row + d_row  # nova pozicija po redu
                new_col = col + d_col  # nova pozicija po koloni
                # ako nova pozicija nije van table i ako nije zid ('w'), ubaci u listu legalnih pozicija
                #if 0 <= new_row < self.board.rows and 0 <= new_col < self.board.cols and self.board.data[new_row][new_col] != 'w':
                if 0 <= new_row < self.board.rows and 0 <= new_col < self.board.cols and self.check_path(new_row, new_col) and self.board.data[new_row][new_col] != 'w':
                    new_positions.append((new_row, new_col))
        return new_positions

    def is_final_state(self):
        return self.position == self.goal_position and self.guns == 2

    def unique_hash(self):
        return str(self.position), str(self.picked_guns), str(self.sensor_area)

    def get_cost(self):
        return (((self.position[0] - self.goal_position[0]) ** 2) + (
                    (self.position[1] - self.goal_position[1]) ** 2)) ** 0.5

    def get_current_cost(self):
        return self.depth

    #funkcija koja proverava da li se zid nalazi na putanji dijagonalnog kretanja (lovac)
    def check_path(self, new_row, new_col):
        row, col = self.position
        if new_row < row:
            if new_col < col:
                for i in range(1, (col - new_col)):
                    if (self.board.data[new_row + i][new_col + i] == 'w'):
                        return False
            elif new_col > col:
                for i in range(1, (new_col - col)):
                    if (self.board.data[new_row + i][new_col - i] == 'w'):
                        return False
        if new_row > row:
            if new_col < col:
                for i in range(1, (col - new_col)):
                    if (self.board.data[new_row - i][new_col + i] == 'w'):
                        return False
            elif new_col > col:
                for i in range(1, (new_col - col)):
                    if (self.board.data[new_row - i][new_col - i] == 'w'):
                        return False
        return True

    def get_legal_positions_medium(self):
        # d_rows (delta rows), d_cols (delta columns)
        # moguci smerovi kretanja robota (desno, levo, dole, gore)
        d_rows = [0, 0, 1, -1, 1, -1, 1, -1]
        d_cols = [1, -1, 0, 0, 1, -1, -1, 1]
        row, col = self.position  # trenutno pozicija

        # kupljenje plavih:
        if self.position not in self.picked_guns and self.guns < 2:
            if self.board.data[row][col] == 'b':
                self.guns += 1
                self.picked_guns.append(self.position)

        # if self.position not in self.sensored_positions and self.position in self.sensor_area:
        #   self.sensored_positions.append(self.position)
        new_positions = []
        # deaktiviranje senzora nakon kupljenja plavih:
        if (self.guns == 2):
            self.sensor_area.clear()

        if self.position not in self.sensor_area and self.position not in self.sensor_area1:
            # normalno kretanje van senzora
            for d_row, d_col in zip(d_rows, d_cols):  # za sve moguce smerove
                new_row = row + d_row  # nova pozicija po redu
                new_col = col + d_col  # nova pozicija po koloni
                # ako nova pozicija nije van table i ako nije zid ('w'), ubaci u listu legalnih pozicija
                if 0 <= new_row < self.board.rows and 0 <= new_col < self.board.cols and self.board.data[new_row][
                    new_col] != 'w' and self.board.data[new_row][new_col] != 's':
                    new_positions.append((new_row, new_col))

        elif self.position in self.sensor_area:
            # cupkanje u mestu, 2 koraka za jedno polje:
            #self.sensor_area.remove(self.position)
            new_positions.append(self.position)
            self.sensor_area[:] = (value for value in self.sensor_area if value != self.position)

        elif self.position in self.sensor_area1:
            # cupkanje u mestu, 2 koraka za jedno polje:
            #self.sensor_area1.remove(self.position)
            new_positions.append(self.position)
            self.sensor_area1[:] = (value for value in self.sensor_area1 if value != self.position)
        else:
            for d_row, d_col in zip(d_rows, d_cols):  # za sve moguce smerove
                new_row = row + d_row  # nova pozicija po redu
                new_col = col + d_col  # nova pozicija po koloni
                # ako nova pozicija nije van table i ako nije zid ('w'), ubaci u listu legalnih pozicija
                if 0 <= new_row < self.board.rows and 0 <= new_col < self.board.cols and self.board.data[new_row][
                    new_col] != 'w' and self.board.data[new_row][new_col] != 's':
                    new_positions.append((new_row, new_col))

        return new_positions

    def find_sensor(self):
        positions = []
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                if self.board.data[row][col] == 's':
                    if self.board.data[row][col] not in positions:
                        positions.append((row, col))
                        positions.append((row+2, col+2))
                        positions.append((row+2, col-2))
                        positions.append((row-2, col+2))
                        positions.append((row-2, col-2))
                        for i in range(1, 4):
                            positions.append((row + i, col))
                            positions.append((row - i, col))
                            positions.append((row, col + i))
                            positions.append((row, col - i))
                            positions.append((row + i, col + 1))
                            positions.append((row + i, col - 1))
                            positions.append((row + 1, col + i))
                            positions.append((row - 1, col + i))
                            positions.append((row - i, col + 1))
                            positions.append((row - i, col - 1))
                            positions.append((row + 1, col - i))
                            positions.append((row - 1, col - i))
        return positions
