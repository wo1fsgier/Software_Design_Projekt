#Hier ist die Speicherlogik für Strukturen, die in der App verwendet wird. 
from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.Knoten import Knoten
from Datenstrukturen.Feder import Feder
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

def load_structure(filename):

    with open(filename, "r") as f:
        data = json.load(f)

    s = Struktur()

    for k in data["Knoten"]:
        massepunkt = Knoten(
            id=k["id"],
            x=k["x"],
            y=k["y"],
        )

        massepunkt.set_force(force_x=k["force_x"], force_y=k["force_y"])

        massepunkt.set_fixed(fixed_x=k["fixed_x"], fixed_y=k["fixed_y"])

        s.add_massepunkt(massepunkt)

    for f in data["Federn"]:
        k1 = s.massepunkte[f["knoten1_id"]]
        k2 = s.massepunkte[f["knoten2_id"]]

        feder = Feder(k1, k2, EA=f["EA"])
        s.add_feder(feder)

    s.loslager_id = data["Loslager_id"]
    s.festlager_id = data["Festlager_id"]
    s.lastknoten_id = data["Lastknoten_id"]

    return s