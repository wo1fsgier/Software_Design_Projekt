import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.StrukturBuilder import StrukturBuilder
from Berechnungen.Optimizer import Optimizer
from Berechnungen.Solver import Solver
from StrukturPlot import plot_structure, on_step, plot_deformed


# ---------------------------Streamlit App --------------------------- #
st.set_page_config(layout="wide")
st.title("Topologieoptimierung") 
if "struktur" not in st.session_state:
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
        #step = st.number_input("Step between points", min_value=0.1, value=10.0, step=0.1)
        #breite = (int(num_x) - 1) * float(step)
        #hoehe  = (int(num_y) - 1) * float(step)
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
            default_loslager_y = s.hoehe
            default_festlager_x = s.breite
            default_festlager_y = s.hoehe
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
            default_kraft_x = s.breite / 2
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
        with st.status("Optimizing... See Results table for live optimization")as status:
            solver = Solver()
            opt = Optimizer(msg=True)
            history = opt.optimize(
                st.session_state["struktur"],
                solver,
                target_fraction_remaining= precentage_remaining,
                max_iter=max_iter,
                remove_per_iter=remove_per_iter,
                on_step=on_step,
                plot_sec=5
                )
            st.session_state["history"] = history
            u, fhg_map = solver.solve_struktur(st.session_state["struktur"])
            st.session_state["u"] = u
            st.session_state["fhg_map"] = fhg_map
            st.session_state["optimized"] = True
            status.update(label="DONE", state="complete")
# --- Ergebnisse --- #
with tab_ergebnis:
    left, right = st.columns([3, 1], gap="large")
    with left:
        st.session_state["plot_box"] = st.empty()
        plot2 = st.empty() 
    with right:
        st.session_state["status_box"] = st.empty()
        stop = st.button ("STOP", use_container_width=True)
        cont =st.button ("Continue", use_container_width=True)
    if st.session_state["optimized"]:
        st.session_state["plot_box"].pyplot(plot_structure(s, "Optimized model"), clear_figure=True)
        u = st.session_state.get("u")
        fhg_map = st.session_state.get("fhg_map")
        max_disp = np.max(np.abs(st.session_state["u"])) 
        scale = 0.05 * max(k.x for k in s.massepunkte.values()) / max_disp # Verschiebung auf 0.5% der Breite skaliert
        if u is not None and fhg_map is not None:
            plot2.pyplot(plot_deformed(s, u, fhg_map, scale), clear_figure=True)
    else:
        st.session_state["plot_box"].pyplot(plot_structure(s, "Current model"), clear_figure=True)

    with right:
        st.subheader("Status")
        st.write("Federn:", len(s.federn))
        st.write("Knoten:", len(s.massepunkte))
# ---------- Debug  ----------
with tab_msg:
    st.subheader("History")