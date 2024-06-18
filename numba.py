import numpy as np
import numba as nb
from numba import njit, prange

N_s = 32  # Spatial extent
N_t = 64  # Temporal extent

beta = 6.0  # Gauge coupling


@njit(fastmath=True)
def lattice_spacing(beta):
    a = 0.1 / beta
    return a

a = lattice_spacing(beta)


@njit(fastmath=True)
def clover_action(gauge_field, beta, a, N_s, N_t):
    action = 0
    for t in prange(N_t):
        for x in prange(N_s):
            for y in prange(N_s):
                for z in prange(N_s):
                    for j in prange(3):
                        for k in prange(3):
                            staple = np.exp(1j * (gauge_field[t, x, y, z, j, k] - gauge_field[t, x, y, z, k, j]))
                            action += beta * (1 - np.real(staple))
    return action


gauge_field = np.zeros((N_t, N_s, N_s, N_s, 3, 3), dtype=np.complex128)

@njit(fastmath=True, parallel=True)
def hmc(gauge_field, beta, a, N_s, N_t, n_steps, max_iterations):
    force = np.zeros((N_t, N_s, N_s, N_s, 3, 3), dtype=np.complex128)
    iteration = 0
    while iteration < max_iterations:
        for i in prange(n_steps):
            for t in prange(N_t):
                for x in prange(N_s):
                    for y in prange(N_s):
                        for z in prange(N_s):
                            for j in prange(3):
                                for k in prange(3):
                                    staple = np.exp(1j * (gauge_field[t, x, y, z, j, k] - gauge_field[t, x, y, z, k, j]))
                                    force[t, x, y, z, j, k] = -beta * np.imag(staple)
           
            gauge_field += a * force
       
        iteration += 1
   
    return gauge_field


n_steps = 10
max_iterations = 1000
gauge_field = hmc(gauge_field, beta, a, N_s, N_t, n_steps, max_iterations)


@njit(fastmath=True, parallel=True)
def plaquette(gauge_field):
    plaquette = 0
    for t in prange(N_t):
        for x in prange(N_s):
            for y in prange(N_s):
                for z in prange(N_s):
                    for j in prange(3):
                        for k in prange(3):
                            plaquette += np.real(gauge_field[t, x, y, z, j, k] * gauge_field[t, x, y, z, j, k].conj())
    return plaquette / (N_t * N_s ** 3 * 6)

print("Plaquette:", plaquette(gauge_field))


ensemble = []
for i in range(n_steps):
    gauge_field = hmc(gauge_field, beta, a, N_s, N_t, n_steps, max_iterations)
    ensemble.append(gauge_field)

print("Ensemble size:", len(ensemble))
