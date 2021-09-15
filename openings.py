"""
Collect information on openings played
"""
from chess_career.extract_game import extract_data
from chess_career.io_module import generate_table_report
from chess_career.extract_game import O_ALL_DATA, O_MYWINS, O_WHITE, O_DRAWS
ECOURL = 'ECOUrl'


def get_my_opening_record(data):
    """
    Args:
        data -- game data extracted

    Returns: List of won/loss info.  Each entry is a list of game numbers
        that are in this category.  The categories in order are: games
        won as white, games drawn as white, games lost as white,
        games won as black, games drwan as black, games lost as black.
    """
    rdict = {}
    for count, entry in enumerate(data[O_ALL_DATA]):
        if ECOURL in entry:
            opening = entry[ECOURL].split("/")[-1]
        else:
            opening = 'Unknown-Opening'
        indx = 0
        if count in data[O_MYWINS]:
            indx += 2
        if count in data[O_DRAWS]:
            indx += 1
        if count not in data[O_WHITE]:
            indx += 3
        if opening not in rdict:
            rdict[opening] = [[], [], [], [], [], []]
        rdict[opening][indx].append(count)
    return rdict


def remove_excess(inchar, opening, loc_val):
    """
    Remove the additional data from an opening name in order to return
    the general name of the opening.

    Args:
        inchar: character to scan for after which all further
                text will be discarded
        opening: full name of the opening
        loc_val: location in opening from which point we should scan for inchar

    Returns;
        Shortened, more general name

    In other words, change 'Sicilian Defense Bowdler Attack'
    to 'Sicilian Defense'
    """
    xloc = opening.find(inchar, loc_val)
    if xloc == -1:
        return opening
    return opening[0:xloc]


def get_openings():
    """
    Find all openings played

    Returns: A list with two entries.  The first entry is a dictionary
    of all games that I have played.  Indexed by full name of the openings,
    the value stored is a list of game numbers matching that opening.
    The second entry is also a dictionary of general openings
    (keys are "Sicilian Defense" rather than all variations of the Sicilian).
    """
    data = extract_data()
    my_rec = get_my_opening_record(data)
    op_list_short = {}
    for entry in my_rec:
        loc_val = 1000
        for keyword in [
                'Defense', 'Opening', 'Game', 'Gambit', 'Attack', 'System'
        ]:
            thisval = entry.find(keyword)
            if thisval > 0:
                if thisval < loc_val:
                    loc_val = thisval
        op_name = remove_excess("-", entry, loc_val)
        op_name = remove_excess(".", op_name, loc_val)
        if op_name not in op_list_short:
            op_list_short[op_name] = [[], [], [], [], [], []]
        for i in range(0, len(op_list_short[op_name])):
            op_list_short[op_name][i].extend(my_rec[entry][i])
    return [my_rec, op_list_short]


def general_opening_info_data(ogroup=""):
    """
    Reformat opening information into a list whose entries are:
    - Number of games
    - Name of opening
    - Win/Loss/Draw record as white (a string)
    - Win/loss/Draw record as black (a string)

    Args:
        ogroup -- Opening name ("Sicilian" for example).
                  General opening names if blank
    """
    otype = 1
    if ogroup:
        otype = 0
    openings = get_openings()[otype]
    op_records = []
    for entry in openings:
        if ogroup:
            if entry.find(ogroup) != 0:
                continue
        gcount = 0
        wlt_data = []
        for indx in (2, 1, 0, 5, 4, 3):
            wldval = len(openings[entry][indx])
            wlt_data.append(wldval)
            gcount += wldval
        op_records.append([entry, wlt_data, gcount])
    slist = sorted(op_records, key=lambda x: x[2], reverse=True)
    return slist


def gen_wdl_string(wld_data):
    """
    Format a list of win, draw, loss values into a dash separated string
    of win, loss, draw values

    Returns: W-L-D string
    """
    return "{}-{}-{}".format(wld_data[0], wld_data[2], wld_data[1])


def generate_opening_report(ogroup=""):
    """
    User interface to generate opening reports.

    Input:
        ogroup -- Opening to search for.  If empty, a general opening
                  search is performed.

    Result:
        In reports sub-directory, an appropriately name file ending with
        "_openings_report" will be generated
    """
    info = general_opening_info_data(ogroup)
    out_lines = []
    for inline in info:
        out_line = []
        out_line.append("{}".format(inline[2]))
        out_line.append(inline[0].replace("-", " "))
        out_line.append(gen_wdl_string(inline[1][0:3]))
        out_line.append(gen_wdl_string(inline[1][3:6]))
        out_lines.append(out_line)
    print(out_lines)
    generate_table_report("general_openings_report", out_lines, ogroup)


if __name__ == "__main__":
    generate_opening_report()
    generate_opening_report("Queens-Pawn")
    generate_opening_report("Kings-Pawn")
    generate_opening_report("Sicilian")
    generate_opening_report("French")
    generate_opening_report("Philidor")
    generate_opening_report("Scotch")
