#Soll die Gesamtstruktur des Feder-Massepunkte Systems darstellen:
#Die Struktur soll Federn und Massepunkte hinzufügen können, den Kraftvektor
#erstellen, die Fixen DOFs bzw. Lager definieren,
#Struktur speichert also alle Informationen über die Struktur, damit sie später vom Solver
#verwendet werden kann

from .Knoten import Knoten
from .Feder import Feder


class Struktur:
    def __init__(self):
        self.federn = [] # Liste der Federn in der Struktur
        self.massepunkte = {} # Dict der Massepunkte in der Struktur {id: knoten}
        self.knoten_federn = {} # Dict der Federn pro Knoten {knoten_id: [federn]}
        self.kraftvektor = None # Kraftvektor für die Struktur
        self.fixe_dofs = [] # Liste der fixen DOFs (Lager)
        self.loslager_id = None
        self.festlager_id = None
        self.loslager_id = None

    def add_feder(self, feder):
        """Registriert eine Feder in der Struktur und aktualisiert die Knoten-Feder-Zuordnung."""
        self.federn.append(feder)
        
        id1 = feder.knoten1.id
        id2 = feder.knoten2.id
        
        # Initialisiere Einträge wenn nötig
        if id1 not in self.knoten_federn:
            self.knoten_federn[id1] = []
        if id2 not in self.knoten_federn:
            self.knoten_federn[id2] = []
        
        # Registriere Feder in beiden Knoten
        self.knoten_federn[id1].append(feder)
        self.knoten_federn[id2].append(feder)

    def add_massepunkt(self, massepunkt):
        self.massepunkte[massepunkt.id] = massepunkt

    def set_kraftvektor(self, kraftvektor):
        self.kraftvektor = kraftvektor

    def set_fixe_dofs(self, fixe_dofs):
        self.fixe_dofs = fixe_dofs

    def remove_knoten(self, knoten_id):
        
        if knoten_id not in self.massepunkte:
            print(f"Warnung: Knoten mit ID {knoten_id} nicht gefunden.")
            return False
        
        # Hole alle Federn dieses Knotens (Kopie, da wir die Liste ändern werden)
        federn_zum_loeschen = self.knoten_federn.get(knoten_id, []).copy()
        
        # Entferne alle Federn, die an diesem Knoten hängen
        for feder in federn_zum_loeschen:
            # Entferne Feder aus globaler Liste
            if feder in self.federn:
                self.federn.remove(feder)
            
            # Entferne Feder aus dem anderen Knoten
            other_id = feder.knoten2.id if feder.knoten1.id == knoten_id else feder.knoten1.id
            if other_id in self.knoten_federn:
                if feder in self.knoten_federn[other_id]:
                    self.knoten_federn[other_id].remove(feder)
        
        # Entferne den Knoten selbst
        del self.massepunkte[knoten_id]
        del self.knoten_federn[knoten_id]
        
        return True

    def get_federn_of_knoten(self, knoten_id):

        return self.knoten_federn.get(knoten_id, [])
    
    def set_knoten_force(self, knoten_id, force_x=0, force_y=0):
        k = self.massepunkte[knoten_id]
        k.force_x = float(force_x)
        k.force_y = float(force_y)
        self.lastknoten_id = knoten_id

    def set_knoten_fixed(self, knoten_id, fixed_x=None, fixed_y=None):
        
        if knoten_id in self.massepunkte:
            self.massepunkte[knoten_id].set_fixed(fixed_x, fixed_y)

    def fix_boundary_nodes(self):

        if not self.massepunkte:
            return
            
        # Finde die x-Grenzen
        x_coords = [k.x for k in self.massepunkte.values()]

        x_min = min(x_coords)
        x_max = max(x_coords)
        
        # Fixiere Knoten an x=0 und x=max
        for knoten in self.massepunkte.values():
            if knoten.x == x_min or knoten.x == x_max:
                knoten.set_fixed(fixed_x=True, fixed_y=True)

    def set_loslager(self, knoten_id):
        self.loslager_id = knoten_id
        self.set_knoten_fixed(knoten_id, fixed_y=True)
    
    def set_festlager(self, knoten_id):
        self.festlager_id = knoten_id
        self.set_knoten_fixed(knoten_id, fixed_x=True, fixed_y=True)

    def unset_knoten_fixed(self, knoten_id):
        k = self.massepunkte.get(knoten_id)
        if k is None:
            return
        k.fixed_x = False
        k.fixed_y = False
    
    
    def unset_knoten_force(self, knoten_id):
        k = self.massepunkte.get(knoten_id)
        if k is None:
            return
        k.force_x = 0.0
        k.force_y = 0.0