import streamlit as st
import matplotlib.pyplot as plt

from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.StrukturBuilder import StrukturBuilder
from Berechnungen.Optimizer import Optimizer
from Berechnungen.Solver import Solver


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

st.title("Topologieoptimierung")

breite = st.number_input("Width of the rectangle", min_value=1, value=600, step=1)
hoehe = st.number_input("Height of the rectangle", min_value=1, value=200, step=1)
num_x = st.number_input("Number of points in horizontal direction", min_value=2, value=61, step=1)
num_y = st.number_input("Number of points in vertical direction", min_value=2, value=21, step=1)
precentage_remaining = st.slider("Target percentage of remaining material", min_value=0.01, max_value=1.0, value=0.39, step=0.01)

if "struktur" not in st.session_state:
    st.session_state["struktur"] = None

if st.button("Create model"):
    struktur = Struktur()

    StrukturBuilder.build_rechteck(
        struktur=struktur,
        breite=breite,
        hoehe=hoehe,
        num_x=int(num_x),
        num_y=int(num_y)
    )
    
    bl = StrukturBuilder.bottom_left_id(struktur)
    br = StrukturBuilder.bottom_right_id(struktur)

    struktur.set_knoten_fixed(bl, fixed_y=True)                 # Loslager
    struktur.set_knoten_fixed(br, fixed_x=True, fixed_y=True)   # Festlager
    top_mid = StrukturBuilder.top_middle_id(struktur)
    struktur.set_knoten_force(top_mid, force_y=100.0) # Kraft 

    st.session_state["struktur"] = struktur
    st.success("Model created")
if "optimized" not in st.session_state:
    st.session_state["optimized"] = False
if st.session_state["struktur"] is not None:
    st.pyplot(plot_structure(st.session_state["struktur"], "Created model"))
    if st.button("Optimize model"):
        solver = Solver()
        opt = Optimizer(msg=True)
        history = opt.optimize(
            st.session_state["struktur"],
            solver,
            target_fraction_remaining= precentage_remaining,
            max_iter=120,
            remove_per_iter=8
        )