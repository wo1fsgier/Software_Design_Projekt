"""StrukturBuilder für die Geometrie-Generierung von Strukturen."""

from .Knoten import Knoten
from .Feder import Feder


class StrukturBuilder:
    """Statische Klassemethoden zum Erstellen verschiedener Strukturgeometrien."""
    
    @staticmethod
    def build_rechteck(struktur, breite, hoehe, num_x, num_y):
        #Erstellt eine Rechtecksgeometrie mit Knoten und Kanten 

        struktur.massepunkte = {}
        struktur.federn = []
        struktur.knoten_federn = {}

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
                y = hoehe - j * dy  # Von oben nach unten aufbauen
                knoten = Knoten(knoten_id, x, y)
                knoten_grid[(i, j)] = knoten
                struktur.massepunkte[knoten_id] = knoten
                knoten_id += 1
        
        # Erstelle Federn zwischen benachbarten Knoten
        for j in range(num_y):
            for i in range(num_x):
                # Horizontale Feder nach rechts
                if i + 1 < num_x:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i+1, j)])
                    struktur.add_feder(feder)
                
                # Vertikale Feder nach unten
                if j + 1 < num_y:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i, j+1)])
                    struktur.add_feder(feder)
                
                # Diagonale Feder nach rechts-unten (45 Grad)
                if i + 1 < num_x and j + 1 < num_y:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i+1, j+1)])
                    struktur.add_feder(feder)
                
                # Diagonale Feder nach links-unten (135 Grad)
                # Nur wenn i > 0, um Doppelungen zu vermeiden
                if i > 0 and j + 1 < num_y:
                    feder = Feder(knoten_grid[(i, j)], knoten_grid[(i-1, j+1)])
                    struktur.add_feder(feder)
