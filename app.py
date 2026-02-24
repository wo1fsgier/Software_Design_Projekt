import streamlit as st
import matplotlib.pyplot as plt

from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.StrukturBuilder import StrukturBuilder


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

col1, col2, col3 = st.columns(3)

num_x = st.number_input("Number of points in horizontal direction", min_value=2, value=61, step=1)
num_y = st.number_input("Number of points in vertical direction", min_value=2, value=21, step=1)
step = st.number_input("Step between points", min_value=0.1, value=10.0, step=0.1)

if "struktur" not in st.session_state:
    st.session_state["struktur"] = None

if st.button("Create model"):
    struktur = Struktur()
    breite = (int(num_x) - 1) * float(step)
    hoehe  = (int(num_y) - 1) * float(step)

    StrukturBuilder.build_rechteck(
        struktur=struktur,
        breite=breite,
        hoehe=hoehe,
        num_x=int(num_x),
        num_y=int(num_y),
    )
    
    st.session_state["struktur"] = struktur
    st.success("Model created.")

if st.session_state["struktur"] is not None:
    st.pyplot(plot_structure(st.session_state["struktur"], "Created model"))
    st.button("Optimize model")