"""
Produce a report of how running out of time adversely affects
the number of games won.
"""
from chess_career.extract_game import (
    extract_data,
    O_ALL_DATA,
    O_DRAW_TYPES,
    O_PLAYER
)
from chess_career.io_module import generate_table_report
from chess_career.utilities import get_times, material
from chess_career.extract_game import USERNAME, TERMINATION
from chess_career.io_module import WHITE
from chess_career.utilities import CURRENT_POSITION
FRAC_FORMAT = "{:.5f}"
LOT_WMA = "Lost on time with material advantage"
LOT_WME = "Lost on time with material equal"
REP_WMA = "Forced repetition with material advantage"
STM_WMA = "Forced stalemate with material advantage"
OOT_OIM = "Out of time where opponent has insufficient material"
REPETITION = "Game drawn by repetition"
STALEMATE = "Game drawn by stalemate"
INSUF_VS_TO = "Game drawn by timeout vs insufficient material"
ON_TIME = "on time"


def get_lead_draws(data, d_type):
    """
    Find draws where we were leading but short on time.

    Input:
        data -- data from extract_game
        d_type -- type of draw (repetition or stalemate)

    Returns a list of draws where we forced the draw, we
    are short of time, and we have a material advantage.
    """
    retval = []
    for gnumb in data[O_DRAW_TYPES][d_type]:
        game_info = data[O_ALL_DATA][gnumb]
        pindex = 1
        if game_info[WHITE][USERNAME] == data[O_PLAYER]:
            pindex = 0
        timevec = get_times(game_info)
        if not timevec:
            continue
        if timevec[pindex] > 200:
            continue
        tomove = game_info[CURRENT_POSITION].split(" ")[1]
        if "wb".find(tomove) + pindex != 1:
            continue
        pdiff = material(game_info)
        if pindex == 1:
            pdiff = 0 - pdiff
        if pdiff <= 0:
            continue
        retval.append(gnumb)
    return retval


def handle_to_vs_insuf(data):
    """
    Handle case where we time out but opponent had insufficient
    material to win.  Since it was not already drawn, assume
    that we had the material to win.

    Args:
        data  -- extract_game data

    Returns: list of games where we have material advantage against
    an opponent with too little material to win, but we drew because
    we ran out of time.
    """
    retval = []
    for gnumb in data[O_DRAW_TYPES][INSUF_VS_TO]:
        game_info = data[O_ALL_DATA][gnumb]
        pindex = 1
        if game_info[WHITE][USERNAME] == data[O_PLAYER]:
            pindex = 0
        tomove = game_info[CURRENT_POSITION].split(" ")[1]
        if "wb".find(tomove) != pindex:
            continue
        retval.append(gnumb)
    return retval


def get_time_issues():
    """
    Get time issues.

    Return a dict indexed by time issue.  Each entry is a list of game
    numbers featuring this issue.
    """
    ret_dict = {
        LOT_WMA: [],
        LOT_WME: [],
        REP_WMA: [],
        STM_WMA: [],
        OOT_OIM: [],
    }
    data = extract_data()
    for count, thisg in enumerate(data[O_ALL_DATA]):
        if not thisg[TERMINATION].startswith(data[O_PLAYER]):
            if thisg[TERMINATION].find(ON_TIME) > 0:
                points = material(thisg)
                if thisg[WHITE][USERNAME] != data[O_PLAYER]:
                    points = 0 - points
                if points > 0:
                    ret_dict[LOT_WMA].append(count)
                if points == 0:
                    ret_dict[LOT_WME].append(count)
    ret_dict[REP_WMA] = get_lead_draws(data, REPETITION)
    ret_dict[STM_WMA] = get_lead_draws(data, STALEMATE)
    ret_dict[OOT_OIM] = handle_to_vs_insuf(data)
    return ret_dict, len(data[O_ALL_DATA])


def generate_time_issue_report():
    """
    User interface to generate report of games with time issues.

    Result:
        In reports sub-directory, a time_issues_report.html file
        will be generated
    """
    info = get_time_issues()
    ginfo = info[0]
    gcount = info[1]
    out_table = []
    extra_wins = 0
    for row in [LOT_WMA, LOT_WME, REP_WMA, STM_WMA, OOT_OIM]:
        out_line = []
        out_line.append(row)
        numb = len(ginfo[row])
        out_line.append("{}".format(numb))
        out_line.append(FRAC_FORMAT.format(numb / gcount))
        if row != LOT_WMA:
            numb /= 2
        extra_wins += numb
        out_table.append(out_line)
    total = ['Additional Wins Possible']
    total.append("{}".format(extra_wins))
    total.append(FRAC_FORMAT.format(extra_wins / gcount))
    out_table.append(total)
    print(out_table)
    generate_table_report("time_issues_report", out_table)


if __name__ == "__main__":
    generate_time_issue_report()
