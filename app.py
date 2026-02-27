import streamlit as st
import matplotlib.pyplot as plt
import os

from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.StrukturBuilder import StrukturBuilder
from Berechnungen.Optimizer import Optimizer
from Berechnungen.Solver import Solver
from StrukturPlot import plot_structure
from Struktur_Speicher import save_structure, load_structure

SAVE_FILE = "saved_model.json"

# ---------------------------Streamlit App --------------------------- #

st.set_page_config(layout="wide")
st.title("Topologieoptimierung") 
if "struktur" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        st.session_state["struktur"] = load_structure(SAVE_FILE)
        st.session_state["optimized"] = False
        st.info("Saved structure loaded.")
    else:
        st.session_state["struktur"] = None
if "optimized" not in st.session_state:
    st.session_state["optimized"] = False
if "history" not in st.session_state:
    st.session_state["history"] = []

# --Sidebar--#

with st.sidebar:
    st.header("Modell")
    with st.form("create_model_form"):
        num_x = st.number_input("Number of points in horizontal direction", min_value=2, value=61, step=1)
        num_y = st.number_input("Number of points in vertical direction", min_value=2, value=21, step=1)
        breite = st.number_input("Width of the structure", min_value=1, value=600, step=1)
        hoehe = st.number_input("Height of the structure", min_value=1, value=200, step=1)
        create = st.form_submit_button("Create model")
    if create:
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

# --- Dashboard --- #
if st.session_state["struktur"] is None:
    st.info("Please create a model first at the left side")
    st.stop()

s = st.session_state["struktur"]
tab_setup, tab_ergebnis, tab_msg = st.tabs(["Boundary Conditions","Results", "Debug"])
with tab_setup:

# --- Randbedingungen --- #

    st.subheader("Boundary Conditions")
    fixed, force = st.columns(2)
    with fixed:
        st.markdown("### Fixations")
        with st.form("fixation_form"):
            default_loslager_x = 0
            default_loslager_y = 0
            default_festlager_x = 0
            default_festlager_y = 0
            loslager_x, festlager_x = st.columns(2)
            with loslager_x:
                los_x = st.number_input("Loslager X", value=default_loslager_x)
                fest_x = st.number_input("Festlager X", value=default_festlager_x) 
            with festlager_x:
                los_y = st.number_input("Loslager Y", value=default_loslager_y)
                fest_y = st.number_input("Festlager Y", value=default_festlager_y)
            set_fixations = st.form_submit_button("Set fixations", use_container_width=True)

        if set_fixations:
            s = st.session_state["struktur"]
            fest_id = StrukturBuilder.set_support(s, s.festlager_id, fest_x, fest_y, s.set_festlager)
            los_id  = StrukturBuilder.set_support(s, s.loslager_id,  los_x,  los_y,  s.set_loslager)

            st.session_state["optimized"] = False
            st.success("Supports updated")

# --- äußere Kräfte --- #

    with force:
        st.markdown("### Forces")
        with st.form("force_form"):
            default_kraft_x = 0
            default_kraft_y = 100
            Position, f = st.columns(2)
            with Position:
                pos_x = st.number_input("Force position in X", value=default_kraft_x)
                pos_y = st.number_input("Force position in Y", value=default_kraft_y)
            with f:
                Fx = st.number_input("Fx", value=0.0, step=10.0)
                Fy = st.number_input("Fy", value=100.0, step=10.0)
            set_force = st.form_submit_button("Set force", use_container_width=True)

        if set_force:
            s = st.session_state["struktur"]
            if s.lastknoten_id is not None:
                s.unset_knoten_force(s.lastknoten_id)
            s.set_knoten_force(
                StrukturBuilder.find_nearest_node_id(s, pos_x, pos_y),
                force_x=Fx,
                force_y=Fy
            )

            st.session_state["optimized"] = False
            st.success("Force updated")
    st.divider()

# --- Optimierung --- #
    st.markdown("### Optimization")
    with st.form("opt_form"):
        t, i, r = st.columns(3)
        with t:
            precentage_remaining = st.slider("Target percentage of remaining material", min_value=0.01, max_value=1.0, value=0.39, step=0.01)
        with i:
            max_iter = st.number_input("Max iterations", min_value=1, value=120, step=1)
        with r:
            remove_per_iter = st.number_input("Elements to remove per iteration", min_value=1, value=8, step=1)

        optimize = st.form_submit_button("Optimize model",use_container_width=True)
    
    if optimize:
        with st.status("Optimizing... This may take a while")as status:
            solver = Solver()
            opt = Optimizer(msg=True)
            history = opt.optimize(
                st.session_state["struktur"],
                solver,
                target_fraction_remaining= precentage_remaining,
                max_iter=max_iter,
                remove_per_iter=remove_per_iter
                )
            st.session_state["history"] = history
            st.session_state["optimized"] = True
            status.update(label="DONE", state="complete")

# --- Ergebnisse --- #
with tab_ergebnis:
    left, right = st.columns([3, 1], gap="large")

    with left:
        if st.session_state["optimized"]:
            st.pyplot(plot_structure(s, "Optimized model"), clear_figure=True)
        else:
            st.pyplot(plot_structure(s, "Current model"), clear_figure=True)

    with right:
        st.subheader("Status")
        st.write("Federn:", len(s.federn))
        st.write("Knoten:", len(s.massepunkte))
        if st.button("Save structure"):
            save_structure(s, "saved_model.json")  # save_structure müsste du noch implementieren
            st.success("Structure saved successfully!")

        if os.path.exists(SAVE_FILE):
            st.write("Saved structure exists.") 
            if st.button("Delete saved structure"):
                os.remove(SAVE_FILE)
                st.success("Saved structure deleted")

# ---------- Debug  ----------
with tab_msg:
    st.subheader("History")