"""
Utility functions
"""
CURRENT_POSITION = "CurrentPosition"
DRAWN = " drawn "
GAMEREC = "gamerec"
CLOCKV = "%clk"
PNAMES = "pnbrq"
POINTS = [1, 3, 3, 5, 9]


def comp_time(movep):
    """
    Compute time value

    Args:
        movep -- text of time information extracted from game log

    Returns time left as an int value of 1/10 second units.
    """
    indx = movep.find("]")
    tparts = movep[0:indx].split(":")
    ptime = int(tparts[0]) * 3600
    ptime += int(tparts[1]) * 60
    if tparts[2].find('.') < 0:
        ptime += int(tparts[2])
        ptime *= 10
    else:
        secs = tparts[2].split(".")
        ptime += int(secs[0])
        ptime *= 10
        ptime += int(secs[1])
    return ptime


def get_times(game):
    """
    Return times of both players

    Arg:
        game -- game data

    Returns: list of two time values (in 1/10 units)
    """
    if CLOCKV in game[GAMEREC]:
        parts = game[GAMEREC].split(' ')
        moves = [x for x in parts if CLOCKV in x]
        times = [x for x in parts if ":" in x]
        if len(moves) == 1:
            secv = [times[-1]]
            secv.append(0)
            return secv
        time1, time2 = times[-2:]
        secv = [comp_time(time1), comp_time(time2)]
        if len(moves) % 2 == 1:
            secv = [secv[1], secv[0]]
        return secv
    return []


def material(game):
    """
    Given a game, return a material count

    Args:
        game -- game data

    returns a material difference. Positive if white is ahead.
    Negative if black is ahead.
    """
    value = 0
    fen_text = game[CURRENT_POSITION].split(" ")[0]
    for cchar in fen_text:
        pvalue = PNAMES.find(cchar.lower())
        if pvalue >= 0:
            if cchar.islower():
                value -= POINTS[pvalue]
            else:
                value += POINTS[pvalue]
    return value
