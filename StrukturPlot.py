from Datenstrukturen import Struktur
import matplotlib.pyplot as plt

def plot_structure(struktur, title="Structure"):
    fig, ax = plt.subplots()

    feder_farbe = "#444444"   # Dunkelgrau
    knoten_farbe = "red"      # Rot

    
    for f in struktur.federn:
        ax.plot(
            [f.knoten1.x, f.knoten2.x],
            [f.knoten1.y, f.knoten2.y],
            color=feder_farbe,
            linewidth=1
        )

    xs = [k.x for k in struktur.massepunkte.values()]
    ys = [k.y for k in struktur.massepunkte.values()]

    ax.scatter(
        xs,
        ys,
        s=20,
        color=knoten_farbe,
        zorder=3   
    )

    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title)
    ax.invert_yaxis()

    fig.tight_layout()
    return fig

   