#Hier ist die Speicherlogik für Strukturen, die in der App verwendet wird. 
from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.Knoten import Knoten
from Datenstrukturen.Feder import Feder
import numpy as np
import json

def save_structure(struktur, filename):

    data = {
        'Knoten': struktur.get_massepunkte(),
        'Federn': struktur.get_federn(),
        'Loslager_id': struktur.loslager_id,
        'Festlager_id': struktur.festlager_id,
        'Lastknoten_id': struktur.lastknoten_id,
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_structure(filename) -> Struktur:
    with open(filename, "r") as f:
        data = json.load(f)

    # Objekt ohne __init__ (Workaround falls __init__ etwas baut)
    s = Struktur.__new__(Struktur)

    # ---- Minimal-sichere Initialisierung ----
    s.massepunkte = {}
    s.federn = []
    s.knoten_federn = {}   # falls add_feder das befüllt

    s.loslager_id = None
    s.festlager_id = None
    s.lastknoten_id = None

    s.breite = 0.0
    s.hoehe = 0.0
    s.num_x = 0
    s.num_y = 0
    s.dx = 0.0
    s.dy = 0.0

    for k in data.get("Knoten", []):
        kn = Knoten(id=k["id"], x=k["x"], y=k["y"])
        kn.set_force(force_x=k.get("force_x", 0.0), force_y=k.get("force_y", 0.0))
        kn.set_fixed(fixed_x=k.get("fixed_x", False), fixed_y=k.get("fixed_y", False))
        s.add_massepunkt(kn)

    for f_ in data.get("Federn", []):
        k1 = s.massepunkte[f_["knoten1_id"]]
        k2 = s.massepunkte[f_["knoten2_id"]]
        feder = Feder(k1, k2, EA=f_.get("EA", None))
        s.add_feder(feder)

    s.loslager_id = data.get("Loslager_id", None)
    s.festlager_id = data.get("Festlager_id", None)
    s.lastknoten_id = data.get("Lastknoten_id", None)

    if s.massepunkte:
        xs = np.array([k.x for k in s.massepunkte.values()], dtype=float)
        ys = np.array([k.y for k in s.massepunkte.values()], dtype=float)
        s.breite = float(xs.max() - xs.min())
        s.hoehe  = float(ys.max() - ys.min())

    return s