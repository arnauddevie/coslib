"""Standard modules"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import ldp


def get_param(filename, time, location=None, delta_t=0.1, delete=None):
    """Fetch parameter data from a given location and time"""
    sheet = ldp.read_csv(filename, start=9, assume=ldp.NUMBER)
    parameter = ldp.load_section(sheet)
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

def j(ce,cse,phie,phis,params,const):
    nice_abs = lambda x: ((np.sign(x)+1)/2)*np.abs(x)

    j0 = lambda ce, cse: params['k_norm_ref']*nice_abs((params['csmax']-cse)/params['csmax'])**(1-params['alpha'])*nice_abs(cse/params['csmax'])**params['alpha']*nice_abs(ce/const['ce0'])**(1-params['alpha'])

    soc = lambda cse: cse/params['csmax']
    eta = lambda cse, phie, phis: phis-phie-params['eref'](soc(cse))
    F = 96487
    R = 8.314
    return j0(ce,cse)*(np.exp((1-params['alpha'])*F*eta(cse, phie, phis)/(R*const['Tref']))-np.exp(-params['alpha']*F*eta(cse,phie,phis)/(R*const['Tref'])))

def main():
    params = dict()
    sheet = ldp.read_excel('../tests/gold_standard/GuAndWang_parameter_list.xlsx', 0)
    (ncol, pcol) = (2,3)
    params['const'] = ldp.load_params(sheet, range(7, 15), ncol, pcol)
    params['neg'] = ldp.load_params(sheet, range(18, 43), ncol, pcol)
    params['sep'] = ldp.load_params(sheet, range(47, 52), ncol, pcol)
    params['pos'] = ldp.load_params(sheet, range(55, 75), ncol, pcol)

    eref_neg = ldp.loadtxt('../tests/gold_standard/eref_neg.csv', comments='%', delimiter=',')
    sheet = ldp.read_csv('../tests/gold_standard/eref_neg.csv', assume=ldp.NUMBER)
    eref_neg = ldp.load_section(sheet)
    sheet = ldp.read_csv('../tests/gold_standard/eref_pos.csv', assume=ldp.NUMBER)
    eref_pos = ldp.load_section(sheet)

    params['neg']['eref'] = lambda soc: np.interp(soc, eref_neg[:][0], eref_neg[:][1])
    params['pos']['eref'] = lambda soc: np.interp(soc, eref_pos[:][0], eref_pos[:][1])

    ce = get_param('../tests/gold_standard/ce.csv', 5)
    cse = get_param('../tests/gold_standard/cse.csv', 5, delete=[80,202])
    phie = get_param('../tests/gold_standard/phie.csv', 5)
    phis = get_param('../tests/gold_standard/phis.csv', 5, delete=[80,202])

    print(j(ce,cse,phie,phis,params['neg'],params['const']))

if __name__ == '__main__':
    sys.exit(main())
