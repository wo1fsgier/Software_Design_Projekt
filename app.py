import io

import streamlit as st
import matplotlib.pyplot as plt
import os
import numpy as np 
from copy import deepcopy 

from Datenstrukturen.Struktur import Struktur
from Datenstrukturen.StrukturBuilder import StrukturBuilder
from Berechnungen.Optimizer import Optimizer
from Berechnungen.Solver import Solver
from StrukturPlot import plot_structure
from Struktur_Speicher import save_structure, load_structure

SAVE_FILE = "saved_model.json"
from StrukturPlot import plot_structure, on_step, plot_deformed, apply_iter_removals


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
if "is_optimizing" not in st.session_state:
    st.session_state["is_optimizing"] = False
if "live_plot_box" not in st.session_state:
    st.session_state["live_plot_box"] = None
if "deformed_box" not in st.session_state:
    st.session_state["deformed_box"] = None
st.session_state.setdefault("plot_box", None)

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
        # -------------------------
        # Standardlager & Kraft setzen
        # -------------------------
        bl = StrukturBuilder.bottom_left_id(struktur)
        br = StrukturBuilder.bottom_right_id(struktur)
        top_mid = StrukturBuilder.top_middle_id(struktur)

        struktur.set_knoten_fixed(bl, fixed_y=True)
        struktur.set_knoten_fixed(br, fixed_x=True, fixed_y=True)
        struktur.set_knoten_force(top_mid, force_y=100.0)

        #Debug-Ausgabe im UI
        st.write("📌 Default Nodes set on creation:")
        st.write(f"Loslager ID: {bl}, x={struktur.massepunkte[bl].x}, y={struktur.massepunkte[bl].y}")
        st.write(f"Festlager ID: {br}, x={struktur.massepunkte[br].x}, y={struktur.massepunkte[br].y}")
        st.write(f"Kraft-Knoten ID: {top_mid}, x={struktur.massepunkte[top_mid].x}, y={struktur.massepunkte[top_mid].y}")

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

            # -------------------------
            # Debug-Ausgabe der manuell gesetzten Fixierungen
            # -------------------------
            st.write("🛠 Manually set nodes:")
            st.write(f"Loslager ID: {los_id}, x={s.massepunkte[los_id].x}, y={s.massepunkte[los_id].y}")
            st.write(f"Festlager ID: {fest_id}, x={s.massepunkte[fest_id].x}, y={s.massepunkte[fest_id].y}")

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

            force_id = StrukturBuilder.find_nearest_node_id(s, pos_x, pos_y)
            s.set_knoten_force(force_id, force_x=Fx, force_y=Fy)

            st.session_state["optimized"] = False
            st.success("Force updated")

            # -------------------------
            # Debug-Ausgabe der manuell gesetzten Kraft
            # -------------------------
            st.write("⚡ Force set on node:")
            st.write(f"Knoten ID: {force_id}, x={s.massepunkte[force_id].x}, y={s.massepunkte[force_id].y}")
            st.write(f"Force vector: Fx={Fx}, Fy={Fy}")

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
        st.session_state["is_optimizing"] = True
        st.session_state["struktur_base"] = deepcopy(st.session_state["struktur"])
        base = deepcopy(st.session_state["struktur"])
        view = deepcopy(base)
        plot_box = st.session_state["live_plot_box"]
        def on_step_live(rec):
            apply_iter_removals(view, rec)
            plot_box.pyplot(
                plot_structure(view, f"Iteration {rec['iter']}"),
                clear_figure=True
            )

        with st.status("Optimizing... See Results table for live optimization")as status:
            solver = Solver()
            opt = Optimizer(msg=True)
            history = opt.optimize(
                st.session_state["struktur"],
                solver,
                target_fraction_remaining= precentage_remaining,
                max_iter=max_iter,
                remove_per_iter=remove_per_iter,
                on_step=on_step_live,
                plot_sec=1
                )
            
            st.session_state["history"] = history
            u, fhg_map = solver.solve_struktur(st.session_state["struktur"])
            st.session_state["u"] = u
            st.session_state["fhg_map"] = fhg_map
            st.session_state["optimized"] = True
            st.session_state["is_optimizing"] = False
            status.update(label="DONE", state="complete")

# --- Ergebnisse --- #
with tab_ergebnis:
    left, right = st.columns([3, 1], gap="large")
   
    with left:
        if st.session_state["optimized"]:

            fig = plot_structure(s, "Optimized model")
        else:
            fig = plot_structure(s, "Current model")

        st.pyplot(fig, clear_figure=False) #True setzen wieder
        if st.session_state["live_plot_box"] is None:
            st.session_state["live_plot_box"] = st.empty()
        plot_box = st.session_state["live_plot_box"]

        if st.session_state["deformed_box"] is None:
            st.session_state["deformed_box"] = st.empty()
        deformed_box = st.session_state["deformed_box"]

    hist = st.session_state.get("history", [])
    base = st.session_state.get("struktur_base")

    with right:
        st.subheader("Status")
        st.write("Federn:", len(s.federn))
        st.write("Knoten:", len(s.massepunkte))

        '''if st.button("Download as SVG"):

            fig = plot_structure(s, "Structure for Download")
            buffer = io.StringIO()
            fig.savefig(buffer, format="svg")
            buffer.seek(0)
    
        st.download_button(
            label="Download structure as SVG",
            data=buffer.getvalue(),
            file_name="structure.svg",
            mime="image/svg+xml"
    )
    plt.close(fig)  # Figur wieder freigeben'''

    st.divider()

    if st.button("Save structure"):
        save_structure(s, "saved_model.json")  # save_structure müsste du noch implementieren
        st.success("Structure saved successfully!")

        if os.path.exists(SAVE_FILE):
            st.write("Saved structure exists.") 
            if st.button("Delete saved structure"):
                os.remove(SAVE_FILE)
                st.success("Saved structure deleted")
        k=0
        if st.session_state["optimized"] and hist:
            max_it = len(hist)
            k = st.slider("Iteration anzeigen", 0, max_it, max_it)
    
    if st.session_state["optimized"]:
        
        if base is None or not hist:
            plot_box.pyplot(plot_structure(s, "Optimized model"), clear_figure=True)
        else:
            
            view = deepcopy(base)
            
            for idx in range(k):
                apply_iter_removals(view, hist[idx])
            plot_box.pyplot(plot_structure(view, f"Iteration {k}"), clear_figure=True)

        if not st.session_state.get("is_optimizing", False):
            u = st.session_state.get("u")
            fhg_map = st.session_state.get("fhg_map")
            max_disp = np.max(np.abs(st.session_state["u"])) 
            scale = 0.05 * max(k.x for k in s.massepunkte.values()) / max_disp # Verschiebung auf 0.5% der Breite skaliert
            if u is not None and fhg_map is not None:
                st.session_state["deformed_box"].pyplot(plot_deformed(s, u, fhg_map, scale),clear_figure=True)
    else:
        plot_box.pyplot(plot_structure(s, "Current model"), clear_figure=True)


# ---------- Debug  ----------
with tab_msg:
    st.subheader("History")