"""
Look at my checkmates
"""
import os
from chess_career.extract_game import extract_data, TERMINATION
from chess_career.io_module import get_header_trailer
from chess_career.utilities import CURRENT_POSITION

from chess_career.extract_game import O_ALL_DATA, O_MYWINS
PERM_ATT_PATH = "permanent_attack_path"
IMPORTANT_PINS = "important_pins"
DEFENSE = "defense"
OFFENSE = "offense"
KINGPOS = "king_location"
BLOCKED = "blocked"
BLKED_DICT = "blked_dict"
BOARD_DIM = 8
OPEN = "open"
OPEN_DICT = "open_dict"
PIECES = "pnbrqk"
MOVE_TABLE = "move_table"
MATERS = "maters"
PINNED = "pinned"
ATTACK_PATH = "attack_path"
KNIGHTS = "nN"
BISHOPS = "bB"
ROOKS = "rR"
KINGS = "kK"
SQUARE_SIZE = 60
PIECE_IMAGE = {
    'P': "0/04/Chess_plt60",
    'R': "5/5c/Chess_rlt60",
    'N': "2/28/Chess_nlt60",
    'B': "9/9b/Chess_blt60",
    'Q': "4/49/Chess_qlt60",
    'K': "3/3b/Chess_klt60",
    'p': "c/cd/Chess_pdt60",
    'r': "a/a0/Chess_rdt60",
    'n': "f/f1/Chess_ndt60",
    'b': "8/81/Chess_bdt60",
    'q': "a/af/Chess_qdt60",
    'k': "e/e3/Chess_kdt60"
}


class Position():
    """
    Save information for a game

    fen_data is the Forsyth-Edwards-Notation information input.

    """
    def __init__(self, fen_data):
        self.board = [['' for _ in range(8)] for _ in range(8)]
        parts = fen_data.split(' ')
        prows = parts[0].split('/')
        for count, rank in enumerate(prows):
            crow = 7 - count
            column = 0
            for fen_char in rank:
                if fen_char.isdigit():
                    column += int(fen_char)
                else:
                    self.board[crow][column] = fen_char
                    column += 1
        self.tomove = parts[1]
        self.out_sections = []
        self.stats = {}
        self.stats[MOVE_TABLE] = {
            "p": self.pawn_move,
            "n": knight_move,
            "k": king_move,
            "b": self.general_move,
            "r": self.general_move,
            "q": self.general_move
        }

    def display_mate(self, counter, noisy=False):
        """
        Display this game's final position

        Input:
            counter -- number of game (used to uniquely create files)
            noisy -- if true, displays crude board on console and
                     waits for input

        outputs an html file in the positions directory
        """
        if self.out_sections == []:
            self.out_sections = get_header_trailer("display_board")
        html_out = []
        for row in range(BOARD_DIM - 1, -1, -1):
            ostring = ''
            for col in range(0, BOARD_DIM):
                if self.board[row][col] == '':
                    if (row + col) % 2 == 0:
                        ostring += '*'
                    else:
                        ostring += '-'
                else:
                    ostring += self.board[row][col]
                    html_out.append(self.gen_img_html(row, col))
            if noisy:
                print(ostring)
        piecelocs = '\n'.join(html_out)
        out_info = '\n'.join([
            self.out_sections[0],
            piecelocs,
            self.out_sections[1]
        ])
        ohtml = "end_position{:05d}.html".format(counter)
        ofile = os.path.join("positions", ohtml)
        with open(ofile, 'w') as iofd:
            iofd.write(out_info)
        if noisy:
            input()

    def gen_img_html(self, row, col):
        """
        Generate an <img> line in the final position html file.

        Input:
            row -- row on board (top is row 7)
            col -- column on board (from 0 to 7)

        Returns the text of an <img> line for the position of a piece.
        """
        oline = ''.join([
            "<img src='https://upload.wikimedia.org/wikipedia/commons/",
            "{}.png' style='position:absolute; top:{}px; left:{}px;'>"
        ])
        piece = PIECE_IMAGE[self.board[row][col]]
        nrow = (BOARD_DIM - row) * SQUARE_SIZE
        ncol = (col + 1) * SQUARE_SIZE
        return oline.format(piece, nrow, ncol)

    def analyze(self):
        """
        Analyze features of this checkmate position.
        """
        if self.tomove == 'b':
            self.stats[DEFENSE] = PIECES
            self.stats[OFFENSE] = PIECES.upper()
        else:
            self.stats[DEFENSE] = PIECES.upper()
            self.stats[OFFENSE] = PIECES
        for row in range(0, BOARD_DIM):
            for col in range(0, BOARD_DIM):
                if self.board[row][col] == "":
                    continue
                if (self.board[row][col] in self.stats[DEFENSE] and
                        self.board[row][col] in KINGS):
                    self.stats[KINGPOS] = [row, col]
                    row = BOARD_DIM
                    break
        self.stats[PERM_ATT_PATH] = []
        self.check_neighborhood()
        self.check_attacks()
        self.resolve_pins()
        if len(self.stats[MATERS]) > 1:
            return "Double Check"
        ploc = self.stats[MATERS][0]
        pinfo = self.board[ploc[0]][ploc[1]]
        if pinfo in KNIGHTS:
            if self.stats[OPEN] == []:
                return "Smother Mate"
        return False

    def check_neighborhood(self):
        """
        Scan area around king and find squares occupied by defenders
        (BLOCKED) or available for the king to move to (OPEN).
        """
        self.stats[BLOCKED] = []
        self.stats[OPEN] = []
        self.stats[PINNED] = []
        self.stats[IMPORTANT_PINS] = []
        self.stats[ATTACK_PATH] = []
        for row in range(-1, 2):
            xcoord = self.stats[KINGPOS][0] + row
            if xcoord < 0 or xcoord >= BOARD_DIM:
                continue
            for col in range(-1, 2):
                if col == 0 and row == 0:
                    continue
                ycoord = self.stats[KINGPOS][1] + col
                if ycoord < 0 or ycoord >= BOARD_DIM:
                    continue
                if self.board[xcoord][ycoord] == "":
                    self.stats[OPEN].append([xcoord, ycoord])
                    continue
                if self.board[xcoord][ycoord] in self.stats[DEFENSE]:
                    self.stats[BLOCKED].append([xcoord, ycoord])
                else:
                    self.stats[OPEN].append([xcoord, ycoord])
        self.stats[MATERS] = []
        self.stats[OPEN_DICT] = {}
        for square in self.stats[OPEN]:
            indx = square[0] * BOARD_DIM + square[1]
            self.stats[OPEN_DICT][indx] = []

    def check_attacks(self):
        """
        Scan board for piece that attack the king and
        its escape squares
        """
        self.stats[BLKED_DICT] = {}
        for row in range(0, BOARD_DIM):
            for col in range(0, BOARD_DIM):
                if self.board[row][col] == "":
                    continue
                if self.board[row][col] in self.stats[OFFENSE]:
                    self.work_out_move([row, col], self.stats[KINGPOS])
                    for nearsq in self.stats[OPEN]:
                        self.work_out_move([row, col], nearsq)

    def work_out_move(self, from_loc, to_loc):
        """
        Collect statistics for the move given
        """
        indx = self.board[from_loc[0]][from_loc[1]].lower()
        if self.stats[MOVE_TABLE][indx](from_loc, to_loc):
            if to_loc == self.stats[KINGPOS]:
                self.stats[MATERS].append(from_loc)
                self.stats[PERM_ATT_PATH] = self.stats[ATTACK_PATH][:]
                self.stats[PERM_ATT_PATH].append(from_loc)
                self.stats[ATTACK_PATH] = []
            else:
                indx1 = to_loc[0] * BOARD_DIM + to_loc[1]
                self.stats[OPEN_DICT][indx1].append(from_loc)

    def pawn_move(self, from_loc, to_loc):
        """
        True if a pawn can move from from_loc to to_loc
        """
        direction = 1
        p_row = from_loc[0] == 1
        p_to_move = self.board[from_loc[0]][from_loc[1]]
        if p_to_move.islower():
            direction = -1
            p_row = from_loc[0] == 6
        take_possible = False
        if to_loc[0] - from_loc[0] == direction:
            if abs(to_loc[1] - from_loc[1]) == 1:
                take_possible = True
        if p_to_move in self.stats[OFFENSE] and not p_to_move == "":
            if take_possible:
                return True
        else:
            if take_possible and self.board[to_loc[0]][to_loc[1]] != '':
                return True
            if to_loc[1] == from_loc[1]:
                if from_loc[0] + direction == to_loc[0]:
                    if self.board[to_loc[0]][to_loc[1]] == '':
                        return True
                if p_row and self.p_doublestep(direction, from_loc, to_loc):
                    return True
        return False

    def p_doublestep(self, direction, from_loc, to_loc):
        """
        Special case for initial pawn moves
        """
        if from_loc[0] + 2 * direction != to_loc[0]:
            return False
        if self.board[from_loc[0] + direction][from_loc[1]] != '':
            return False
        if self.board[to_loc[0] + 2 * direction][to_loc[1]] != '':
            return False
        return True

    def general_move(self, from_loc, to_loc):
        """
        Handle orthogonal and diagonal moves
        """
        xdiff = to_loc[0] - from_loc[0]
        ydiff = to_loc[1] - from_loc[1]
        factor = abs(xdiff)
        if factor == 0:
            factor = abs(ydiff)
        if abs(xdiff) == abs(ydiff):
            if self.board[from_loc[0]][from_loc[1]] not in ROOKS:
                return self.check_between(from_loc, to_loc)
        if xdiff * ydiff == 0:
            if self.board[from_loc[0]][from_loc[1]] not in BISHOPS:
                return self.check_between(from_loc, to_loc)
        return False

    def check_between(self, from_loc, to_loc):
        """
        Insure blanks spaces between squares in a long
        directional move.  Collect pinned piece information too.
        """
        if from_loc == to_loc:
            return False
        xdiff = to_loc[0] - from_loc[0]
        ydiff = to_loc[1] - from_loc[1]
        factor = max([abs(xdiff), abs(ydiff)])
        xdiff //= factor
        ydiff //= factor
        if factor == 1:
            return True
        chk_loc = to_loc[:]
        factor -= 1
        interf = []
        while factor > 0:
            factor -= 1
            chk_loc[0] -= xdiff
            chk_loc[1] -= ydiff
            if chk_loc == self.stats[KINGPOS]:
                continue
            if self.board[chk_loc[0]][chk_loc[1]] == '':
                if to_loc == self.stats[KINGPOS]:
                    self.stats[ATTACK_PATH].append(chk_loc[:])
                continue
            interf.append(chk_loc[:])
        if not interf:
            return True
        self.stats[ATTACK_PATH] = []
        if len(interf) > 1:
            return False
        iloc = interf[0]
        if self.board[iloc[0]][iloc[1]] == "":
            return False
        if self.board[iloc[0]][iloc[1]] in self.stats[DEFENSE]:
            if to_loc == self.stats[KINGPOS]:
                self.stats[PINNED].append([from_loc, iloc])
        return False

    def resolve_pins(self):
        """
        Handle cases where a piece cannot capture or interpose
        because it is pinned
        """
        if len(self.stats[MATERS]) > 1:
            return
        for entry in self.stats[PINNED]:
            pindp = entry[1]
            indx = self.board[pindp[0]][pindp[1]].lower()
            for lto_loc in self.stats[PERM_ATT_PATH]:
                if self.stats[MOVE_TABLE][indx](pindp, lto_loc):
                    self.stats[IMPORTANT_PINS].append(entry)
                    break


def knight_move(from_loc, to_loc):
    """
    True if a knight at from_loc can move to to_loc
    """
    xdim = from_loc[0] - to_loc[0]
    ydim = from_loc[1] - to_loc[1]
    if abs(xdim * ydim) == 2:
        return True
    return False


def king_move(from_loc, to_loc):
    """
    True if a king at from_loc can move to to_loc
    """
    if abs(from_loc[0] - to_loc[0]) > 1:
        return False
    if abs(from_loc[1] - to_loc[1]) > 1:
        return False
    return True


def collect_my_mates():
    """
    Run the display_mate program on all my checkmates.
    """
    data = extract_data()
    for gnumb in data[O_MYWINS]:
        game = data[O_ALL_DATA][gnumb]
        if game[TERMINATION].endswith("checkmate"):
            endpos = Position(game[CURRENT_POSITION])
            endpos.display_mate(gnumb)
            ostr = endpos.analyze()
            if ostr:
                ostr += " -- " + game['white']['username'] + " vs "
                ostr += game['black']['username'] + " " + game["Date"]
                ostr += " (" + str(gnumb) + ")"
                print(ostr)


if __name__ == "__main__":
    collect_my_mates()
