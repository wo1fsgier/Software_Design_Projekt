from Datenstrukturen.Struktur import Struktur
from Berechnungen.Optimizer import Optimizer
import matplotlib.pyplot as plt
import streamlit as st

def plot_structure(struktur, title="Structure"):
    fig, ax = plt.subplots()

    feder_farbe = "#444444"   # Dunkelgrau
    knoten_farbe = "red"      # Rot

    
    for f in struktur.federn:
        ax.plot([f.knoten1.x, f.knoten2.x], [f.knoten1.y, f.knoten2.y], color="red", linewidth=1)
    xs = [k.x for k in struktur.massepunkte.values()]
    ys = [k.y for k in struktur.massepunkte.values()]
    ax.scatter(xs, ys, s=10, color="blue")
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title)
    ax.invert_yaxis()
    return fig

def on_step(it, struktur):
    plot_box = st.session_state.get("plot_box")
    if plot_box is None:
        return
    plot_box.pyplot(plot_structure(struktur, f"Iter {it}"), clear_figure=True)

def plot_deformed(struktur, u, fhg_map, scale):
    fig, ax = plt.subplots()

    for f in struktur.federn:
        i, j = f.knoten1.id, f.knoten2.id
        bi, bj = fhg_map[i], fhg_map[j]
        # Original
        x_orig = [f.knoten1.x, f.knoten2.x]
        y_orig = [f.knoten1.y, f.knoten2.y]
        ax.plot(x_orig, y_orig, color="lightgray", linewidth=1)
        # Deformiert
        x_def = [f.knoten1.x + scale * u[bi], f.knoten2.x + scale * u[bj]]
        y_def = [f.knoten1.y + scale * u[bi + 1], f.knoten2.y + scale * u[bj + 1]]
        ax.plot(x_def, y_def, color="red", linewidth=2)

    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_title("Deformed model")
    return fig

def apply_iter_removals(struktur, hist_entry):
    for nid in hist_entry.get("removed_ids", []):
        if nid in struktur.massepunkte:
            struktur.remove_knoten(nid)
