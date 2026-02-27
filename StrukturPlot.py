from Datenstrukturen.Struktur import Struktur
from Berechnungen.Optimizer import Optimizer
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors
def plot_structure(struktur, title="Structure"):
    fig, ax = plt.subplots()
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

def plot_stress_structure(struktur, u, fhg_map, scale=1.0):

    fig, ax = plt.subplots()
    all_nodes = list(struktur.massepunkte.values())
    xs_all = np.array([k.x for k in all_nodes], dtype=float)
    ys_all = np.array([k.y for k in all_nodes], dtype=float)
    ax.scatter(xs_all, ys_all, s=6, c="lightgrey", alpha=0.35, linewidths=0)
    node_imp = {k.id: 0.0 for k in all_nodes}

    for f in struktur.federn:
        i = f.knoten1.id
        j = f.knoten2.id

        bi = fhg_map[i]
        bj = fhg_map[j]

        dux = u[bi] - u[bj]
        duy = u[bi + 1] - u[bj + 1]

        c, s, L = f.direction()
        delta = c * dux + s * duy
        N = f.k() * delta

        val = abs(float(N))
        node_imp[i] += val
        node_imp[j] += val
        ax.plot([f.knoten1.x, f.knoten2.x], [f.knoten1.y, f.knoten2.y],
                color="black", alpha=0.08, linewidth=1)

    imp = np.array([node_imp[k.id] for k in all_nodes], dtype=float)

    if np.all(imp <= 0):
        ax.set_aspect("equal", adjustable="box")
        ax.invert_yaxis()
        ax.set_title("Node importance (all zero)")
        return fig

    max_imp = float(imp.max())
    pos = imp[imp > 0]
    vmin = float(pos.min()) if pos.size else max_imp * 1e-6
    vmin = max(vmin, max_imp * 1e-3) 
    norm = colors.LogNorm(vmin=vmin, vmax=max_imp)
    cmap = cm.get_cmap("plasma")
    mask = imp > 0
    ax.scatter(xs_all[mask], ys_all[mask],
               s=18, c=imp[mask], cmap=cmap, norm=norm,
               alpha=0.95, linewidths=0)
    ax.set_aspect("equal", adjustable="box")
    ax.invert_yaxis()
    ax.set_title("Node importance")
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=ax)
    cbar.set_label("Node importance")
    return fig