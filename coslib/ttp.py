"""Standard modules"""
import sys
import numpy as np
import ldp
import matplotlib.pyplot as plt


class SimMesh(object):
    def __init__(self, mesh, neg, sep, pos):
        self.mesh = mesh
        self.neg = neg
        self.pos = pos
        self.sep = sep


class SimData(object):
    def __init__(self, ce, cse, phie, phis, j):
        self.ce = ce
        self.cse = cse
        self.phie = phie
        self.phis = phis
        self.j = j

    def get_sim_data(self, time_index, location):
        return SimData(
                self.ce[time_index, location], self.cse[time_index, location],
                self.phie[time_index, location], self.phis[time_index, location],
                self.j[time_index, location])

def get_var(parameter, time, location=None, delta_t=0.1, delete=None):
    """Fetch parameter data from a given location and time"""
    (x_parameter, y_parameter) = (parameter[:, 0], parameter[:, 1])
    time_frame = np.nonzero(np.diff(x_parameter) < 0)[0]
    start = np.insert(time_frame+1, 0, 0)
    stop = np.append(time_frame, len(x_parameter))
    time_range = np.arange(0, len(start))*delta_t
    time_index = np.nonzero(time_range == time)[0][0]
    data = y_parameter[start[time_index]:stop[time_index]+1]
    if location:
        data = data[
            location == x_parameter[start[time_index]:stop[time_index]]]

    if delete:
        data = np.delete(data, delete)

    return np.array([data])


def nice_abs(number):
    """Return the absolute of the given number"""
    return ((np.sign(number)+1)/2)*np.abs(number)


def reaction_flux(sim_data, params, const):
    """J"""

    reaction_flux0 = params['k_norm_ref'] * \
        nice_abs((params['csmax']-sim_data.cse)/params['csmax']) ** \
        (1-params['alpha']) * \
        nice_abs(sim_data.cse/params['csmax']) ** params['alpha'] * \
        nice_abs(sim_data.ce/const['ce0']) ** (1-params['alpha'])

    soc = sim_data.cse/params['csmax']
    # eta = phis-phie-params['eref'](soc)
    eta = sim_data.phis-sim_data.phie-params['Uocp'][0](soc)
    F = 96487
    R = 8.314
    return np.array([reaction_flux0*(
        np.exp((1-params['alpha'])*F*eta/(R*const['Tref'])) -
        np.exp(-params['alpha']*F*eta/(R*const['Tref'])))])


def region(mesh):
    """Find the regions in the mesh"""
    xneg = np.nonzero(mesh <= 1)[0]
    xpos = np.nonzero(mesh > 2)[0]
    xsep = np.nonzero((mesh > 1) & (mesh <= 2))[0]

    if mesh[xneg[-1]] == mesh[xneg[-2]]:
        xsep = np.concatenate((1, xneg[-1], xsep))
        xneg = np.delete(xneg, -1)

    if mesh[xsep[-1]] == mesh[xsep[-2]]:
        xpos = np.concatenate((1, xsep[-1], xpos))
        xsep = np.delete(xsep, -1)

    return SimMesh(mesh, xneg, xsep, xpos)


def assemble_comsol(time, data, space=None, dt=0.1):
    ce, cse, phie, phis, j = (np.empty((0, len(data['mesh']))) for i in range(5))
    for ind in time:
        ce = np.append(ce, get_var(data['ce'], ind), axis=0)
        cse = np.append(cse, get_var(data['cse'], ind, delete=[80, 202]), axis=0)
        phie = np.append(phie, get_var(data['phie'], ind), axis=0)
        phis = np.append(phis, get_var(data['phis'], ind, delete=[80, 202]), axis=0)
        j = np.append(j, get_var(data['j'], ind, delete=[80, 202]), axis=0)

    return SimData(ce, cse, phie, phis, j)


def plot_j(time, data, mesh, params):
    jneg = np.empty((0, len(mesh.neg)))
    jpos = np.empty((0, len(mesh.pos)))

    for ind in range(0,len(time)):
        jneg = np.append(jneg, reaction_flux(data.get_sim_data(ind, mesh.neg), params['neg'], params['const']), axis=0)
        jpos = np.append(jpos, reaction_flux(data.get_sim_data(ind, mesh.pos), params['pos'], params['const']), axis=0)
        plt.plot(mesh.neg, jneg[ind,:], mesh.pos, jpos[ind,:])

    print('Neg rms: {}'.format(np.sqrt(np.mean(np.square(jneg-data.get_sim_data(slice(0,len(time)), mesh.neg).j), axis=1))))
    print('Pos rms: {}'.format(np.sqrt(np.mean(np.square(jpos-data.get_sim_data(slice(0,len(time)), mesh.pos).j), axis=1))))
    plt.grid()
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.show()


def main():
    print('Loading Cell Parameters')
    params = dict()
    time = [5, 15, 25, 35, 45]
    sheet = ldp.read_excel(
        '../tests/gold_standard/GuAndWang_parameter_list.xlsx', 0)
    (ncol, pcol) = (2, 3)
    params['const'] = ldp.load_params(sheet, range(7, 15), ncol, pcol)
    params['neg'] = ldp.load_params(sheet, range(18, 43), ncol, pcol)
    params['sep'] = ldp.load_params(sheet, range(47, 52), ncol, pcol)
    params['pos'] = ldp.load_params(sheet, range(55, 75), ncol, pcol)

    comsol = ldp.load('../tests/gold_standard/guwang2.npz')

    comsol_parsed = assemble_comsol(time, comsol)

    comsol_mesh = region(comsol['mesh'])
    plot_j(time, comsol_parsed, comsol_mesh, params)

    return
    ce = get_var(comsol['ce'], 5)
    cse = get_var(comsol['cse'], 5, delete=[80, 202])
    phie = get_var(comsol['phie'], 5)
    phis = get_var(comsol['phis'], 5, delete=[80, 202])
    mesh_neg, mesh_sep, mesh_pos = region(comsol['mesh'])
    print(mesh_neg)

    print(reaction_flux(ce, cse, phie, phis, params['neg'], params['const']))

if __name__ == '__main__':
    sys.exit(main())
