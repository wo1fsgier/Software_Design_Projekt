from Datenstrukturen import Struktur
import matplotlib.pyplot as plt


def plot_structure(struktur, title="Structure"):
    fig, ax = plt.subplots()
    for f in struktur.federn:
        ax.plot([f.knoten1.x, f.knoten2.x], [f.knoten1.y, f.knoten2.y])
    xs = [k.x for k in struktur.massepunkte.values()]
    ys = [k.y for k in struktur.massepunkte.values()]
    ax.scatter(xs, ys, s=10)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title)
    ax.invert_yaxis()
    return fig