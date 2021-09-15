"""
Read json files in data directory and collect a complete
list of games.
"""
import configparser
import datetime
import json
import os
from chess_career.io_module import copy_files, DEFAULT, DATA_PATH, JSON
from chess_career.utilities import GAMEREC, CURRENT_POSITION
from chess_career.io_module import BLACK, WHITE, DATE
USER = "user"
ENDTIME = "EndTime"
O_ALL_DATA = "all_data"
O_DRAW_TYPES = "draw_types"
O_DRAWS = "draws"
O_MYWINS = "mywins"
O_PLAYER = "player"
O_WHITE = "awhite"
O_WININFO = "wininfo"
O_WLASTMV = "wlastmv"
PGN = "pgn"
GAMES = "games"
DRAWN = "drawn"
USERNAME = "username"
TERMINATION = "Termination"


def restruct(entry):
    """
    Reformat a game and associate each game with a timestamp
    so that sorting produces a definitive order of games.

    Returns a tuple consisting of:
        timestamp -- in seconds
        a reformmated dictionary of game information

    Args:
        entry -- game object
    """
    sdata = {}
    sdata[WHITE] = entry[WHITE]
    sdata[BLACK] = entry[BLACK]
    sinfo = entry[PGN].split(']')
    sdata[GAMEREC] = entry[PGN].split("\n\n")[-1].strip()
    for pair in sinfo:
        spair = pair.strip()
        apair = spair.split(' ')
        back_part = " ".join(apair[1:])
        if apair[0].startswith('['):
            akey = apair[0][1:]
            adata = back_part.strip('"')
            sdata[akey] = adata
    dayinfo = sdata[DATE].split(".")
    timeinfo = sdata[ENDTIME].split(":")
    new_dict_key = int(datetime.datetime(
        int(dayinfo[0]), int(dayinfo[1]), int(dayinfo[2]),
        int(timeinfo[0]), int(timeinfo[1]), int(timeinfo[2])
    ).timestamp())
    return new_dict_key, sdata


def get_all_game_data():
    """
    Return list of all games played (each entry is a dictionary)
    representing data
    """
    return_list = []
    file_list = []
    j_locs = os.listdir(DATA_PATH)
    for jfile in j_locs:
        if jfile.endswith(JSON):
            file_list.append(os.path.join(DATA_PATH, jfile))
    file_list = sorted(file_list)
    for jfile in file_list:
        month_dict = {}
        month_list = []
        with open(jfile, 'r') as jfile_fd:
            glist = json.load(jfile_fd)
            for entry in glist[GAMES]:
                mkey, mdata = restruct(entry)
                month_dict[mkey] = mdata
        klist = sorted(month_dict.keys())
        for indx in klist:
            month_list.append(month_dict[indx])
        return_list.extend(month_list)
    return return_list


def extract_data():
    """
    Main data extraction routine.  Returns a dictionary containing
    the following entries:

    O_PLAYER -- player name
    O_DRAW_TYPES -- a dictionary indexed by reasons for a draw.
                  The value is a matching list of game numbers
    O_WININFO -- a dictionary indexed by type of win (checkmate,
               resignation, time control). Each value is a list of
               game numbers with this result.
    O_MYWINS -- a list of games that I won.
    O_WHITE -- a list of games in which I played white.
    O_WLASTMV -- a list of games where white was the last side to move.
    O_DRAWS -- a list of drawn games.
    O_ALL_DATA -- a list of full games.  The index of a specific game
                is its game number
    """
    pinfo = copy_files(configparser.ConfigParser())
    all_data = get_all_game_data()
    outres = {}
    outres[O_PLAYER] = pinfo[DEFAULT][USER]
    outres[O_DRAW_TYPES] = {}
    outres[O_WININFO] = {}
    outres[O_MYWINS] = []
    outres[O_WHITE] = []
    outres[O_WLASTMV] = []
    for count, game in enumerate(all_data):
        if game[WHITE][USERNAME] == outres[O_PLAYER]:
            outres[O_WHITE].append(count)
        result = game[TERMINATION]
        tomove = game[CURRENT_POSITION].split(' ')[1]
        if tomove == 'b':
            outres[O_WLASTMV].append(count)
        if DRAWN in result:
            outres[O_DRAW_TYPES].setdefault(result, []).append(count)
        else:
            if result.startswith(pinfo[DEFAULT][USER] + " "):
                outres[O_MYWINS].append(count)
            skip_pl = result.find(" ")
            np_result = result[skip_pl + 1:]
            outres[O_WININFO].setdefault(np_result, []).append(count)
    outres[O_DRAWS] = []
    for tdraws in outres[O_DRAW_TYPES]:
        outres[O_DRAWS].extend(outres[O_DRAW_TYPES][tdraws])
    outres[O_ALL_DATA] = all_data
    return outres
