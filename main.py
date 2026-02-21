


from Datenstrukturen.Struktur import Struktur

print("Hello World")

# Teste das Rechteck mit Grid
struktur = Struktur()
struktur.build_rechteck(breite=10, hoehe=5, num_x=5, num_y=3)

print("\n=== INITIAL ===")
print(f"Anzahl Knoten: {len(struktur.massepunkte)}")
print(f"Anzahl Federn: {len(struktur.federn)}")

print("\nKnoten (mit Kräften und Fixierungen):")
for id, knoten in sorted(struktur.massepunkte.items()):
    print(f"  Knoten {id}: ({knoten.x}, {knoten.y}) - Fx={knoten.force_x}, Fy={knoten.force_y}, Fixed=({knoten.fixed_x}, {knoten.fixed_y}) - {len(knoten.federn)} Federn")

# Test: Randbedingungen setzen
print("\n=== RANDKNOTEN FIXIEREN ===")
struktur.fix_boundary_nodes()

print("Nach Fixierung der Randknoten:")
for id, knoten in sorted(struktur.massepunkte.items()):
    if knoten.fixed_x or knoten.fixed_y:
        print(f"  Knoten {id}: Fixed=({knoten.fixed_x}, {knoten.fixed_y})")

# Test: Kräfte setzen
print("\n=== KRÄFTE SETZEN ===")
struktur.set_knoten_force(7, force_x=10.0, force_y=-5.0)  # Kraft auf Knoten 7
struktur.set_knoten_force(12, force_y=15.0)  # Nur y-Kraft auf Knoten 12

print("Knoten mit Kräften:")
for id, knoten in sorted(struktur.massepunkte.items()):
    if knoten.force_x != 0 or knoten.force_y != 0:
        print(f"  Knoten {id}: Fx={knoten.force_x}, Fy={knoten.force_y}")

print("\nFedern:")
for i, feder in enumerate(struktur.federn):
    print(f"  {i}: Knoten {feder.knoten1.id} -- Knoten {feder.knoten2.id}")

# Test: Entferne einen Knoten
print("\n=== NACH ENTFERNEN VON KNOTEN 5 ===")
struktur.remove_knoten(5)

print(f"Anzahl Knoten: {len(struktur.massepunkte)}")
print(f"Anzahl Federn: {len(struktur.federn)}")

print("\nVerbleibende Knoten:")
for id, knoten in sorted(struktur.massepunkte.items()):
    print(f"  Knoten {id}: ({knoten.x}, {knoten.y}) - Fx={knoten.force_x}, Fy={knoten.force_y}, Fixed=({knoten.fixed_x}, {knoten.fixed_y}) - {len(knoten.federn)} Federn")

print("\nVerbleibende Federn:")
for i, feder in enumerate(struktur.federn):
    print(f"  {i}: Knoten {feder.knoten1.id} -- Knoten {feder.knoten2.id}")