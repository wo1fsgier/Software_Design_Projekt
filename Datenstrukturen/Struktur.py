#Soll die Gesamtstruktur von Federn darstellen:
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
        self.kraftvektor = None # Kraftvektor für die Struktur
        self.fixe_dofs = [] # Liste der fixen DOFs (Lager)

    def add_feder(self, feder):
        self.federn.append(feder)

    def add_massepunkt(self, massepunkt):
        self.massepunkte[massepunkt.id] = massepunkt

    def set_kraftvektor(self, kraftvektor):
        self.kraftvektor = kraftvektor

    def set_fixe_dofs(self, fixe_dofs):
        self.fixe_dofs = fixe_dofs

    def build_rechteck(self, breite, hoehe, num_x, num_y):
        """Erstellt eine rechteckige Struktur mit gleichmäßig verteilten Knoten.
        
        Die Knoten werden in einem regelmäßigen Grid-Muster platziert, sodass die äußeren
        Grenzen EXAKT bei (0,0) bis (breite, hoehe) liegen. Benachbarte Knoten werden durch
        Federn verbunden (horizontal, vertikal und diagonal für 45-Grad-Winkel).
        
        Parameters
        ----------
        breite : float
            Breite des Rechtecks.
        hoehe : float
            Höhe des Rechtecks.
        num_x : int
            Anzahl der Knoten in x-Richtung (mindestens 1).
        num_y : int
            Anzahl der Knoten in y-Richtung (mindestens 1).
        """
        self.massepunkte = {}
        self.federn = []

        if num_x < 1 or num_y < 1:
            raise ValueError("num_x und num_y müssen mindestens 1 sein.")
        
        # Berechne gleichmäßige Schrittweiten
        dx = breite / (num_x - 1) if num_x > 1 else 0
        dy = hoehe / (num_y - 1) if num_y > 1 else 0
        
        print(f"Grid: {num_x} × {num_y} Knoten")
        print(f"Schrittweiten: dx={dx:.4f}, dy={dy:.4f}")
        
        # Erstelle Knoten in einem Grid
        knoten_grid = {}  # Dict für schnellen Zugriff: (i, j) -> Knoten
        knoten_id = 0
        
        for j in range(num_y):
            for i in range(num_x):
                x = i * dx
                y = j * dy
                knoten = Knoten(knoten_id, x, y)
                knoten_grid[(i, j)] = knoten
                self.massepunkte[knoten_id] = knoten
                knoten_id += 1
        
        # Erstelle Federn zwischen benachbarten Knoten
        for j in range(num_y):
            for i in range(num_x):
                # Horizontale Feder nach rechts
                if i + 1 < num_x:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i+1, j)])
                    self.federn.append(feder)
                
                # Vertikale Feder nach unten
                if j + 1 < num_y:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i, j+1)])
                    self.federn.append(feder)
                
                # Diagonale Feder nach rechts-unten (45 Grad)
                if i + 1 < num_x and j + 1 < num_y:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i+1, j+1)])
                    self.federn.append(feder)
                
                # Diagonale Feder nach links-unten (135 Grad)
                # Nur wenn i > 0, um Doppelungen zu vermeiden
                if i > 0 and j + 1 < num_y:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i-1, j+1)])
                    self.federn.append(feder)

    def remove_knoten(self, knoten_id):
        
        if knoten_id not in self.massepunkte:
            print(f"Warnung: Knoten mit ID {knoten_id} nicht gefunden.")
            return False
        
        knoten = self.massepunkte[knoten_id]
        
        # Erstelle eine Kopie der Feder-Liste, da wir sie während der Iteration ändern
        federn_zum_loeschen = list(knoten.federn)
        
        # Entferne alle Federn, die an diesem Knoten hängen
        for feder in federn_zum_loeschen:
            feder.remove_from_nodes()  # Entfernt Feder aus beiden Knoten
            if feder in self.federn:
                self.federn.remove(feder)
        
        # Entferne den Knoten selbst
        del self.massepunkte[knoten_id]
        
        return True

    def set_knoten_force(self, knoten_id, force_x=None, force_y=None):
        
        if knoten_id in self.massepunkte:
            self.massepunkte[knoten_id].set_force(force_x, force_y)

    def set_knoten_fixed(self, knoten_id, fixed_x=None, fixed_y=None):
        
        if knoten_id in self.massepunkte:
            self.massepunkte[knoten_id].set_fixed(fixed_x, fixed_y)

    def fix_boundary_nodes(self):
        """Fixiert alle Knoten an den seitlichen Rändern (x=0 und x=max).
        
        Für ein Rechteck-Gitter werden nur die Knoten in der ersten und letzten 
        Spalte (bezüglich x-Richtung) fixiert. Dies entspricht typischen Lagerungen
        an den Seiten einer Struktur.
        """
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

    
