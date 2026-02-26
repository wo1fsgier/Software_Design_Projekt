"""StrukturBuilder für die Geometrie-Generierung von Strukturen."""

from .Knoten import Knoten
from .Feder import Feder
from .Struktur import Struktur


class StrukturBuilder:

    @staticmethod
    def bottom_left_id(struktur):
        
        return min(struktur.massepunkte.values(), key=lambda k: (-k.y, k.x)).id
    
    @staticmethod
    def find_nearest_node_id(struktur, x, y):
        return min(struktur.massepunkte.values(),
            key=lambda k: (k.x - x) ** 2 + (k.y - y) ** 2).id
    
    @staticmethod
    def set_support(s, old_id, x, y, setter):
        if old_id is not None:
            s.unset_knoten_fixed(old_id)
        new_id = StrukturBuilder.find_nearest_node_id(s, x, y)
        setter(new_id)
        return new_id

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
        struktur.breite = breite
        struktur.hoehe = hoehe
        struktur.num_x = num_x
        struktur.num_y = num_y

        if num_x < 1 or num_y < 1:
            raise ValueError("num_x und num_y müssen mindestens 1 sein.")
        
        struktur.dx = breite / (num_x - 1) if num_x > 1 else 0
        struktur.dy = hoehe / (num_y - 1) if num_y > 1 else 0
        
        print(f"Grid: {num_x} × {num_y} Knoten")
        print(f"Schrittweiten: dx={struktur.dx:.4f}, dy={struktur.dy:.4f}")
        
        # Erstellt die Knoten in einem Grid
        knoten_grid = {}  
        knoten_id = 0
        
        for j in range(num_y):
            for i in range(num_x):
                x = i * struktur.dx
                y = struktur.hoehe - j * struktur.dy  
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
        