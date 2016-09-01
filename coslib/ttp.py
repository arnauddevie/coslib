"""Standard modules"""
import numpy as np
import ldp

"""
def load(filename, start=1):
    Load CSV data assuming floating numbers
    values = list()
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            values.append(row)

    return np.array(values[start-1:], dtype='float')
"""


def get_param(filename, time, location=None, delta_t=0.1, delete=None):
    """Fetch parameter data from a given location and time"""
    sheet = ldp.read_csv(filename, start=9, assume=ldp.NUMBER)
    parameter = ldp.read_section(sheet)
    (x_parameter, y_parameter) = (parameter[:, 0], parameter[:, 1])
    time_frame = np.nonzero(np.diff(x_parameter) < 0)[0]
    start = np.insert(time_frame+1, 0, 1)
    stop = np.append(time_frame, len(x_parameter))
    time_range = np.arange(0, len(start))*delta_t
    time_index = np.nonzero(time_range == time)[0][0]
    data = y_parameter[start[time_index]:stop[time_index]+1]
    if location:
        data = data[
            location == x_parameter[start[time_index]:stop[time_index]]]

    if delete:
        data = np.delete(data, delete)

    return data
