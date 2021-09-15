"""
Produce pages of game information.  Each page corresponds to a game.
Information displayed on the page includes game number, date, opening,
players, and a record of themoves.
"""
import os
from datetime import datetime
from chess_career.extract_game import (
    extract_data,
    GAMEREC,
    O_ALL_DATA,
    USERNAME
)
from chess_career.io_module import (
    WHITE,
    BLACK,
    DATE
)
from chess_career.io_module import write_game_page, NUMBER, OPENING
from chess_career.openings import ECOURL


def generate_game_page(info_packet):
    """
    Extracts the record from a game packet, formats the moves into
    rows of cells, and calls write_game_page to produce the file.

    Parameters:
        info_packet -- dict of game information/metadata
    """
    adj_gm_rec = info_packet[GAMEREC].split(" ")
    new_gm_rec = adj_gm_rec[0:-1]
    new_gm_rec[-1] = ' '.join([new_gm_rec[-1], adj_gm_rec[-1]])
    move_data = []
    this_mv = []
    for mv_info in new_gm_rec:
        this_mv.append(mv_info)
        if len(this_mv) == 3:
            move_data.append(this_mv)
            this_mv = []
    if len(this_mv) > 0:
        move_data.append(this_mv)
    write_game_page(info_packet, move_data)


def refmt_date(in_date):
    """
    Covert format of the date:

    indate -- yyyy.mm.day
    returns -- date formatted like: July 4, 2021
    """
    dfmt = '#'
    if os.name.endswith('ix'):
        dfmt = '-'
    fmt_str = ' '.join(['%B', '%{}d,'.format(dfmt), '%Y'])
    return datetime.strptime(in_date, '%Y.%m.%d').strftime(fmt_str)


def move_fix(move_list):
    """
    Reformat the move information by removing the time information
    and breaking sections with "..." into one line.

    move_list -- move information
    returns -- newly formatted move information
    """
    if "..." in move_list:
        new_moves = []
        mlist = move_list.split(' ')
        for xmove in mlist:
            if xmove.endswith("..."):
                continue
            if xmove.startswith("{"):
                continue
            if xmove.endswith("}"):
                continue
            new_moves.append(xmove)
        return ' '.join(new_moves)
    return move_list


def write_game_info():
    """
    Loop through all games and produce a page for each game.
    """
    game_data = extract_data()
    for count, game_info in enumerate(game_data[O_ALL_DATA]):
        info_packet = {}
        info_packet[NUMBER] = count
        info_packet[WHITE] = game_info[WHITE][USERNAME]
        info_packet[BLACK] = game_info[BLACK][USERNAME]
        info_packet[DATE] = refmt_date(game_info[DATE])
        if ECOURL not in game_info:
            continue
        info_packet[OPENING] = game_info[ECOURL]
        info_packet[GAMEREC] = move_fix(game_info[GAMEREC])
        generate_game_page(info_packet)


if __name__ == "__main__":
    write_game_info()
