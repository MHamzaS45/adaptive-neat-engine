import streamlit as st
import threading
import time

from wheelspin import AdaptationWheel

st.set_page_config(
    page_title="Adaptive Neuroevolution Engine",
    layout="wide",
)

st.title("Adaptive Neuroevolution Engine Dashboard")

# Session state variables
if "wheel_running" not in st.session_state:
    st.session_state.wheel_running = False
if "thread" not in st.session_state:
    st.session_state.thread = None
if "wheel" not in st.session_state:
    st.session_state.wheel = None
if "played_sound" not in st.session_state:
    st.session_state.played_sound = False

# Dashboard layout
st.sidebar.header("Engine Configuration")
config_path = st.sidebar.text_input(
    "NEAT Config",
    value="config-feedforward.ini",   
)



if st.button("Turn the Wheel"):

    if (
        st.session_state.thread is None
        or not st.session_state.thread.is_alive()
    ):
        wheel = AdaptationWheel(
            config_path
        )

# Session state variables to persist across reruns
        st.session_state.wheel = wheel
        st.session_state.thread = threading.Thread(target=wheel.run_full_adaptation,daemon=True,)
        st.session_state.thread.start()
        st.session_state.wheel_running = True
        st.session_state.played_sound = False


chart_placeholder = st.empty()
status_placeholder = st.empty()

thread = st.session_state.thread
wheel = st.session_state.wheel

if thread is not None:

    if thread.is_alive():
        status_placeholder.info("Evolution running...")
        if (wheel is not None and len(wheel.topology_history) > 0):
            fitness = [x["fitness"] for x in wheel.topology_history]
            chart_placeholder.line_chart(fitness)
        time.sleep(1)
        st.rerun()

    else:
        status_placeholder.success("ADAPTATION COMPLETE")
        if (wheel is not None and len(wheel.topology_history) > 0):
            fitness = [
                x["fitness"]
                for x in wheel.topology_history
            ]
            chart_placeholder.line_chart(fitness)

# Sound
        if not st.session_state.played_sound:
            try:
                with open("sfx.mp3", "rb") as f:
                    st.audio(
                        f.read(),
                        format="audio/mp3",
                        autoplay=True,
                    )
            except FileNotFoundError:
                st.warning("sfx.mp3 not found.")
            st.session_state.played_sound = True


if (wheel is not None and len(wheel.adaptation_log) > 0):
    st.subheader("Adaptation Log")
    st.dataframe(wheel.adaptation_log)

if (wheel is not None and len(wheel.topology_history) > 0):
    st.subheader("Topology History")
    st.dataframe(wheel.topology_history)