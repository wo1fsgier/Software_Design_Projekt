import math

class Optimizer:
    def __init__(self, msg=False):
        self.msg = msg

    def optimize(self, struktur, solver, target_fraction_remaining=0.39, max_iter=100, remove_per_iter=12, on_step=None, plot_sec=5):
        n0 = len(struktur.massepunkte)
        target_n = max(4, int(math.ceil(n0 * target_fraction_remaining))) # target_n grenze

        history = []

        for it in range(1, max_iter + 1): # jede Interation = einmal Optimieren

            n_now = len(struktur.massepunkte)
            if n_now <= target_n: # stoppt wenn Grenze erreicht
                break

            u, fhg_map = solver.solve_struktur(struktur)
            if u is None:
                break

            K, F, randbedingungen, fhg_map = solver.calculate(struktur)
            compliance = sum(u[i] * F[i] for i in range(len(u))) # Skalarprodukt

            W = solver.knoten_signifikanz(struktur, u, fhg_map) # Energiesumme aller Feder die an diesem Knoten hängen

            if on_step is not None and (it % plot_sec == 0):
                    on_step(it, struktur)
            candidates = sorted(W.items(), key=lambda kv: kv[1]) # Liste nach Energie

            removed = 0
            removed_ids = []
            
            for i, E in candidates:

                if len(struktur.massepunkte) <= target_n: # stoppt wenn Grenze erreicht
                    break

                if removed >= remove_per_iter:  # stoppt wenn genug gelöscht
                    break

                k = struktur.massepunkte.get(i) #Knoten
                if k is None:
                    continue

                # backup damit das Löschen wieder rückgängig gemacht werden kann
                backup = self._remove_node_temp(struktur, i)

                # Fällt die Struktur auseinander? Wenn ja, dann kann das Backup restored werden
                if not self._is_connected(struktur):
                    self._restore_node(struktur, backup)
                    continue

                removed += 1
                
                removed_ids.append(i)

                if self.msg:
                    print(f"Iter {it}: removed {i}") #Debug-Ausgabe zur Kontrolle
                
                history.append({
                    "iter": it,
                    "n_nodes": n_now,
                    "removed_ids": removed_ids,
                })
                if on_step is not None and (it % plot_sec == 0):
                    on_step(it, struktur)  

        return history


    def _remove_node_temp(self, struktur, i):# entfernt Knoten und deren Federn
        node = struktur.massepunkte[i]
        federn = struktur.knoten_federn.get(i, []).copy()

        struktur.remove_knoten(i)

        return (i, node, federn)

    def _restore_node(self, struktur, backup): # restorefunktion falls die Struktur auseinanderfällt --> Backup
        i, node, federn = backup

        struktur.massepunkte[i] = node
        struktur.knoten_federn[i] = []

        for feder in federn:
            struktur.federn.append(feder)
            struktur.knoten_federn[i].append(feder)

            other = feder.knoten2.id if feder.knoten1.id == i else feder.knoten1.id
            if other not in struktur.knoten_federn:
                struktur.knoten_federn[other] = []
            struktur.knoten_federn[other].append(feder)

    def _is_connected(self, struktur):

        x = {i: set() for i in struktur.massepunkte.keys()} # für jeden Knoten alle Nachbarn die über die Feder verbunden sind

        for feder in struktur.federn:
            i = feder.knoten1.id
            j = feder.knoten2.id
            if i in x and j in x:
                x[i].add(j)
                x[j].add(i)

        start = next(iter(x))
        visited = {start} # Alle Knoten die schon erreicht wurden
        stack = [start]# ALle Knoten die noch besucht werden müssen

        while stack:
            v = stack.pop()
            for w in x[v]:
                if w not in visited:
                    visited.add(w)
                    stack.append(w)

        return len(visited) == len(x)