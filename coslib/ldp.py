"""Required modules"""
import re
import csv
import sys
import numpy as np
import scipy.io as sio
import xlrd

DATE = xlrd.XL_CELL_DATE
TEXT = xlrd.XL_CELL_TEXT
BLANK = xlrd.XL_CELL_BLANK
EMPTY = xlrd.XL_CELL_EMPTY
ERROR = xlrd.XL_CELL_ERROR
NUMBER = xlrd.XL_CELL_NUMBER


class Spreadsheet:
    """Hold spreadsheet data"""

    def __init__(self, assumption=None):
        """Entry point for :class:`Spreadsheet`"""
        self.values = None
        self.ctypes = None
        self.assume = assumption

    def set_data(self, data_in):
        """Set spreadsheet data using cell generators"""
        data = list(data_in)
        self.values = [[col.value for col in row] for row in data]
        self.ctypes = [[col.ctype for col in row] for row in data]

    def set_values(self, values):
        """Set spreadsheet cell values

        :param values: values to set
        :type values: container, e.g. list"""
        self.values = values

    def set_ctypes(self, ctype):
        """Set spreadsheet cell types. I.e. NUMBER, TEXT, etc.

        :param ctype: cell types to set
        :type values: container, e.g. list"""
        self.ctypes = ctype

    def size(self):
        """Retrieve the dimensions of the spreadsheet

        :return: spreadsheed dimensions
        :rtype: tuple"""
        if self.values is not None:
            return len(self.values), len(self.values[0])
        else:
            return None

    def cell(self, xpos, ypos):
        """Retrieve cell information

        :param xpos: cell row
        :param ypos: cell column
        :type xpos: integer
        :type ypos: integer
        :return: cell values and info
        :rtype: :class:`xlrd.sheet.Cell`"""
        if self.ctypes:
            return xlrd.sheet.Cell(
                self.ctypes[xpos][ypos], self.values[xpos][ypos])
        elif self.assume:
            return xlrd.sheet.Cell(self.assume, self.values[xpos][ypos])
        else:
            return None


def read_xl(filename, sheet=None, sheet_type='name'):
    """Read sheet data or sheet names from an Excel workbook

    :example:

    sheet_names = read_xl('parameter.xlsx') # returns a list of sheet names

    :example:

    spreadsheet = read_xl('parameter.xlsx', 0, 'index')
    # returns the sheet data return ``Sheet Names`` if the given *sheet* is set
    # to None, return sheet data otherwise.

    :param filename: name of the excel woorkbook to import
    :param sheet: spreadsheet name or index to import
    :param type: using 'index' or 'name' for designating a sheet
    :type filename: string
    :type sheet: string or integer or None
    :type name: string
    :return: sheet names if sheet is None, otherwise sheet data
    :rtype: list of strings if sheet is None, otherwise :class:`Spreadsheet`"""
    book = xlrd.open_workbook(filename)
    spreadsheet = Spreadsheet()
    if sheet is None:
        return book.sheet_names()
    elif sheet_type == 'name':
        xl_sheet = book.sheet_by_name(sheet)
        spreadsheet.set_data(xl_sheet.get_rows())
        return spreadsheet
    elif sheet_type == 'index':
        xl_sheet = book.sheet_by_index(sheet)
        spreadsheet.set_data(xl_sheet.get_rows())
        return spreadsheet
    else:
        return None


def read_csv(filename, start=1, stop=None, assume=TEXT):
    """Read a csv file into a :class:`Spreadsheet`

    :example:

    sheet = read_csv('parameters.csv', start=9, assume=NUMBER)

    :param filename: name of the file to read
    :param start: row to start reading
    :param stop: row to stop reading
    :param assume: type of data to assume
    :type filename: string
    :type start: integer
    :type stop: integer
    :type assume: integeri
    :return: spreadsheet data
    :rtype: :class:`Spreadsheet`"""
    values = []
    spreadsheet = Spreadsheet(assume)
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            values.append(row)

    if stop is None:
        stop = len(values)

    values = values[start-1:stop]
    spreadsheet.set_values(values)
    return spreadsheet


def read_mat(filename, variable):
    """Read the variable *variable* from *filename*

    :example:

    sheet = read_mat("parameter.mat", "cse")

    :param filename: name of the .mat file to read
    :param variable: variable to load
    :type filename: string
    :type variable: string
    :return: variable data
    :rtype: array"""
    contents = sio.loadmat(filename)
    return contents[variable]


def read_section(sheet, row_range=None, col_range=None):
    """Read a 'chunk' of data from a spreadsheet.

    Given a selection of rows and columns, this function will return the
    intersection of the two ranges. Note that the minimum value for each range
    is 1.

    :example:

    spreadsheet = read_xl('parameters.xlsx', 'Parameters')
    cell_data = read_section(
        spreadsheet, [1, 3, 5], range(7, 42))

    :param sheet: spreadsheet data
    :param row_range: selected rows
    :param col_range: selected columns
    :type sheet: :class:`xlrd.sheet`
    :type row_range: list of integers
    :type col_range: list of integers
    :return: section of sheet data
    :rtype: array if assume=NUMBER else list"""

    if row_range is None:
        row_range = range(1, len(sheet.values)+1)

    if col_range is None:
        col_range = range(1, len(sheet.values[0])+1)

    rval = [[sheet.cell(x-1, y-1) for y in col_range] for x in row_range]

    if sheet.assume == NUMBER:
        return np.array(
            [[rval[x-1][y-1].value for y in col_range] for x in row_range],
            dtype='float')

    return rval


def _multiple_replace(repl, text):
    """Replace multiple regex expressions

    :param repl: dictionary of values to replace
    :param text: text to perform regex on
    :type repl: dict
    :type text: string
    :return: processed text
    :rtype: string"""
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, repl.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: repl[mo.string[mo.start():mo.end()]], text)


def _fun_to_lambda(entry):
    """Convert a given string representing a matlab anonymous
    function to a lambda function

    :example:
    lambdafun = "@(x) cos(x)"
    lambdafun(np.pi)

    :param entry: string of matlab anonymous equation
    :type: string
    :return: mathmatical function
    :rtype: lambda function"""
    repl = {
        'sin': 'np.sin',
        'cos': 'np.cos',
        'tan': 'np.tan',
        'sech': '1/np.cosh',
        'exp': 'np.exp',
        './': '/',
        '.*': '*',
        '.^': '**'
    }

    # pull out function variable definition
    vari = re.findall(r'\@\(.*?\)', entry)
    vari = [re.sub(r'\@|\(|\)', '', x) for x in vari]

    # remove variable definition
    entry = re.sub(r'\@\(.*?\)', '', entry)

    # replace operators to suit numpy
    entry = _multiple_replace(repl, entry)

    # separate equations into different functions
    entry = re.sub('{|}', '', entry).split(',')

    return list(
        eval('lambda ' + vari[i] + ': ' + entry[i])
        for i in range(0, len(entry)))


def read_params(sheet, name_rrange, name_crange, param_rrange, param_crange):
    """Read designated parameters from the sheet

    :example:

    sheet=read_xl('parameter_list.xlsx', 0, 'index')
    params["pos"] = read_params(sheet, range(55, 75), [2], range(55, 75), [3])

    :param sheet: spreadsheet data
    :param name_rrange: cell rows to read for parameter names
    :param name_crange: cell columns to read for parameter names
    :param param_rrange: cell rows to read for parameter data
    :param param_crange: cell columns to read for parameter data
    :type sheet: :class:`Spreadsheet`
    :type name_rrange: list of integers
    :type name_crange: list of integers
    :type param_rrange: list of integers
    :type param_crange: list of integers
    :return: mapping of parameter names to values
    :rtype: dict"""

    name_cells = read_section(sheet, name_rrange, name_crange)
    data_cells = read_section(sheet, param_rrange, param_crange)

    # Verify the number of names matches the number of params
    assert len(name_cells) == len(data_cells)

    data = [_fun_to_lambda(x.value) if x.ctype == TEXT else
            x.value if x.ctype == NUMBER else None
            for y in data_cells for x in y]

    return dict(zip([x.value for y in name_cells for x in y], data))


def main():
    pass

if __name__ == '__main__':
    sys.exit(main())
