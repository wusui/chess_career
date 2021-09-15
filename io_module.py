"""
I/O Modules used by chess tools
"""
import os
import shutil
DATA_PATH = os.path.join("..", "..", "data")
DEFAULT = "DEFAULT"
FROMDIR = "fromdir"
JSON = ".json"
NUMBER = "number"
OPENING = "opening"
BLACK = "black"
WHITE = "white"
DATE = "Date"


def copy_files(conf_info):
    """
    Copy files from fromfile field read from an ini file.

    Args:
        conf_info -- configparser object
    """
    conf_info.read("chess.ini")
    if FROMDIR in conf_info[DEFAULT]:
        for file_name in os.listdir(conf_info[DEFAULT][FROMDIR]):
            if file_name.startswith('y') and file_name.endswith(JSON):
                shutil.copy(
                    os.sep.join([conf_info[DEFAULT][FROMDIR], file_name]),
                    DATA_PATH
                )
    return conf_info


def format_table(array_of_entries):
    """
    Format a set of lines into html code for those lines in a table.

    Args:
        array_of_entries -- list of lines that make up the table

    Returns:
        String of HTML lines that represent rows in the table.
    """
    out_lines = []
    for in_line in array_of_entries:
        wrap_parts = []
        for part in in_line:
            wrap_parts.append("".join(['<td>', part, '</td>']))
        nline = "".join(["<tr>", "".join(wrap_parts), "</tr>"])
        out_lines.append(nline)
    return "".join(out_lines)


def assemble_table_rows(template_file, array_of_entries):
    """
    Format the table portion of a page.

    Input:
        template_file: File containing skeleton html code for a page.
                       The data in the table rows replace the
                       DATA_GOES_HERE line
        array_of_entries: List of lists. Each entry represents a row.
                       Each entry within a row represets a cell.

    Returns:
        Text for an html page with the table is inserted.
    """
    header, trailer = get_header_trailer(template_file)
    block_of_data = format_table(array_of_entries)
    return ''.join([header, block_of_data, trailer])


def generate_table_report(template_file, array_of_entries, specific=""):
    """
    Generate a page display of a table

    Args:
        template_file -- a file in the ./templates directory (with the txt
                         suffix added).  This file contains most of the html
                         data for the file to be geneated.  The text
                         DATA_GOES_HERE will get replaced by table entries
        array_of_entries -- List of lines.  Each line is a list of column
                            values ( table cells).
        specific -- Name of the html_file, if specified. Text also gets
                    inserted in header instead of "General".

    Output:
        html file displaying the table is written to the reports directory
    """
    output = assemble_table_rows(template_file, array_of_entries)
    ofilen = template_file
    if specific:
        output = output.replace("General", specific)
        ofilen = ofilen.replace("general", specific)
    ofile = os.path.join("reports", ofilen + ".html")
    with open(ofile, 'w') as iofd:
        iofd.write(output)


def get_header_trailer(template_file):
    """
    Split up a template file into the first half and second half

    Input:
        template_file -- text file of templated html code

    Returns: front text of html page, back text of html page
    """
    if os.sep in template_file:
        tfile = template_file
    else:
        tfile = "{}{}{}.txt".format("templates", os.sep, template_file)
    with open(tfile, 'r') as iofd:
        html_data = iofd.read()
    brk_loc = html_data.find("DATA_GOES_HERE")
    header = html_data[0:brk_loc]
    trailer = html_data[brk_loc:]
    blank = trailer.find('\n')
    trailer = trailer[blank:]
    return header, trailer


def write_game_page(info_packet, tbl_info):
    """
    Create a game page in the game subdiretory

    Parameters:
        info_packet -- dict of information about the game.
                    (opening, date, number, players)
        tbl_info -- move information going into the table.
                    format is a list of lists.  Each top
                    level list is a row represented by
                    a list of cells.
    """
    print(info_packet, tbl_info)
    template_file = "game_page"
    output = assemble_table_rows(template_file, tbl_info)
    gnumber = info_packet[NUMBER] + 1
    ofilen = "".join(['game', str(gnumber).zfill(5)])
    output = output.replace("GAME_NUMBER", str(gnumber))
    output = output.replace("GAME_DATE", info_packet[DATE])
    topening = info_packet[OPENING].split("/")[-1]
    output = output.replace("GAME_OPENING", topening)
    output = output.replace("GAME_WHITE", info_packet[WHITE])
    output = output.replace("GAME_BLACK", info_packet[BLACK])
    ofile = os.path.join("games", ofilen + ".html")
    with open(ofile, 'w') as iofd:
        iofd.write(output)
