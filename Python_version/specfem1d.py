#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 10:30:04 2013

Main script for 1D spectral elements.
    u(z,t) = sum(ui(t)li(z)) for i=1...nSpec*(N+1)
    with  nSpec  : number of elements:
         N+1  : number of basis functions per element
         li(z): Lagrange polynomial of degree N
    ->   ui(t): Time dependent expansion coeffs (what we are looking for)

   The parameters of the run can be edited in the file Par_file

@author: Alexis Bottero, CNRS Marseille, France (alexis.bottero@gmail.com)
"""

import numpy as np

from config import Parameter
from config import Source
import functions        # Contains fundamental functions
from grid import OneDimensionalGrid

### --- MAIN BODY --- ###
# Initialization
param=Parameter()    # Initialize all the parameters of the run. Store them
grid = OneDimensionalGrid(param)
if param.plot:
    grid.plot()

param.dt = functions.estimate_timestep(grid, param)
source=Source(param) # Initialize the source
if param.plot:
    source.plotSource()

# Computation of stiffness matrices
Ke = functions.make_stiffness_matrix(grid, param)

# Computation of global mass matrices
M = functions.make_mass_matrix(grid, param)

# Time integration
u=np.zeros(param.nGlob,dtype='d')
vel,acc=np.zeros_like(u),np.zeros_like(u)

if param.plot:
    import matplotlib.pyplot as plt
    plt.ion()
    fig = plt.figure()
    plt.hold(False)

if param.axisym and (param.plot or param.snapshot):
    cz = np.concatenate((-grid.z[:0:-1], grid.z))

# Main time loop :
for it in range(param.nts):
    print 'it = ',it,' (t = ',it*param.dt,'s)'
    if it > 0:
        u += param.dt * vel + acc * param.dt**2 / 2
        vel += param.dt / 2 * acc
        acc.fill(0)

    for e in range(param.nSpec):
        acc[param.ibool[e,:]] -= np.dot(Ke[e,:,:], u[param.ibool[e,:]])

    acc[param.iSource] += source[it*param.dt]
#    # Boundary conditions :
#    acc[0] = 0.
#    acc[len(acc)-1] = 0.
    acc /= M
    vel += param.dt / 2 * acc

    if param.snapshot and (it % param.snapshot == 0 or it == param.nts - 1):
        name = 'snapshot_forward_normal%05d' % (it, )
        if param.axisym:
            c = np.concatenate((u[:0:-1], u))
            np.savetxt(name, np.column_stack((cz, c)))
        else:
            np.savetxt(name, np.column_stack((grid.z, u)))

    if param.plot and it % param.dplot == 0:
        if param.axisym:
            c = np.concatenate((u[:0:-1], u))
            plt.plot(cz,c)
            plt.xlim([-max(grid.z),max(grid.z)])
            plt.ylim([-10,10]) #plt.ylim([0,0.01])
            plt.grid(True)
        else:
            plt.plot(grid.z,u)
            plt.ylim([-0.10,0.10]) #plt.ylim([0,0.01])
        plt.title("it : {}".format(it))
        plt.draw()

