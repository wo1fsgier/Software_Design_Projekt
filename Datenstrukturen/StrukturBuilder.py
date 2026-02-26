"""StrukturBuilder für die Geometrie-Generierung von Strukturen."""

from .Knoten import Knoten
from .Feder import Feder
from .Struktur import Struktur


class StrukturBuilder:

    @staticmethod
    def bottom_left_id(struktur):
        
        return min(struktur.massepunkte.values(), key=lambda k: (-k.y, k.x)).id

    @staticmethod
    def bottom_right_id(struktur):
        
        return min(struktur.massepunkte.values(), key=lambda k: (-k.y, -k.x)).id

    @staticmethod
    def top_middle_id(struktur):
       
        # obere Reihe auswählen (Toleranz gegen Rundungsfehler)
        y_min = min(k.y for k in struktur.massepunkte.values())
        top = [k for k in struktur.massepunkte.values()
               if abs(k.y - y_min) < 1e-12]
        if not top:
            raise ValueError("Struktur enthält keine Knoten")

        top.sort(key=lambda k: k.x)
        mid_index = len(top) // 2
        if len(top) % 2 == 0:
            mid_index -= 1
        return top[mid_index].id

    #Statische Klassemethoden zum Erstellen verschiedener Strukturgeometrien.
    @staticmethod
    def build_rechteck(struktur, breite, hoehe, num_x, num_y):
        #Erstellt eine freie Rechtecksgeometrie mit Knoten und Kanten 

        struktur.massepunkte = {}
        struktur.federn = []
        struktur.knoten_federn = {}

        if num_x < 1 or num_y < 1:
            raise ValueError("num_x und num_y müssen mindestens 1 sein.")
        
        
        dx = breite / (num_x - 1) if num_x > 1 else 0
        dy = hoehe / (num_y - 1) if num_y > 1 else 0
        
        print(f"Grid: {num_x} × {num_y} Knoten")
        print(f"Schrittweiten: dx={dx:.4f}, dy={dy:.4f}")
        
        # Erstellt die Knoten in einem Grid
        knoten_grid = {}  
        knoten_id = 0
        
        for j in range(num_y):
            for i in range(num_x):
                x = i * dx
                y = hoehe - j * dy  
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
        