import numpy as np
from .Solver_Test_1 import solve as solve_lin


class Solver:
    def __init__(self):
        pass
    def calculate(self, struktur):
        knoten_ids = sorted(struktur.massepunkte.keys())
        n = len(knoten_ids)
        fhg_map= {knoten_id: 2*i for i, knoten_id in enumerate(knoten_ids)}
        knoten_fhg = 2*n
        K = np.zeros((knoten_fhg, knoten_fhg))
        F = np.zeros(knoten_fhg)
        randbedingungen = []

        for knoten_id in knoten_ids:
            knoten = struktur.massepunkte[knoten_id]
            b = fhg_map [knoten_id]
            F[b] += knoten.force_x
            F[b+1] += knoten.force_y

            if knoten.fixed_x:
                randbedingungen.append(b)
            if knoten.fixed_y:
                randbedingungen.append(b+1)
        
        for feder in struktur.federn:
            i = feder.knoten1.id
            j = feder.knoten2.id
            if i not in fhg_map or j not in fhg_map:
                continue
            bi = fhg_map[i]
            bj = fhg_map[j]
            fhgs = (bi, bi+1, bj, bj+1)
            k = feder.matrix()

            for a in range(4):
                for b in range (4):
                    K[fhgs[a], fhgs[b]] += k[a, b]
        return K, F, randbedingungen, fhg_map
        
    def solve_struktur(self, struktur):
        K,F, randbedingungen, fhg_map = self.calculate(struktur)
        print("K shape:", K.shape)
        print("F shape:", F.shape)
        u = solve_lin(K.copy(), F.copy(), randbedingungen)
        return u, fhg_map

    def feder_energie(self, feder, u, fhg_map):
        i = feder.knoten1.id
        j = feder.knoten2.id
        bi = fhg_map[i]
        bj = fhg_map[j]
        dux = u[bi] - u[bj]
        duy = u[bi+1] - u[bj+1]
        c, s, L = feder.direction()
        delta = c*dux + s*duy
        k = feder.k()
        E = 0.5 *k *delta**2
        return E
    
    def knoten_signifikanz(self, struktur, u, fhg_map):
        W = {knoten_id: 0 for knoten_id in fhg_map.keys()}
        for feder in struktur.federn:
            i = feder.knoten1.id
            j = feder.knoten2.id
            if i not in fhg_map or j not in fhg_map:
                continue
            E =Solver.feder_energie(self, feder, u, fhg_map)
            W[i] += E
            W[j] += E
        return W