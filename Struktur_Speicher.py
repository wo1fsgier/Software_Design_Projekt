#Hier ist die Speicherlogik für Strukturen, die in der App verwendet wird. 
from Datenstrukturen.Struktur import Struktur
import json

def save_structure(struktur, filename):

    data = {
        'Knoten': struktur.get_massepunkte(),
        'Federn': struktur.get_federn(),
        'Loslager_id': struktur.loslager_id,
        'Festlager_id': struktur.festlager_id,
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)