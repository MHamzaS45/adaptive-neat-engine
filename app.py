
import streamlit as st
import threading
import time
import os 

from wheel import AdaptationWheel

st.title("Adaptive Neuroevolution Engine Dashboard")

# 1. Initialize persistent session state
if "wheel_running" not in st.session_state:
    st.session_state.wheel_running = False
if "latest_stats" not in st.session_state:
    st.session_state.latest_stats = []

# 2. Add control widgets
pop_size = st.sidebar.slider("Population Size", 50, 300, 150)
config_path = st.sidebar.text_input("Configuration Path", "config.yaml")

# 3. Create a background execution trigger
if st.button("Turn the Wheel"):
    if not st.session_state.wheel_running:
        st.session_state.wheel_running = True
        
        # Instantiate your orchestrator
        wheel = AdaptationWheel(config_path, pop_size=pop_size)
        
        # Start evolution in a non-blocking background thread
        thread = threading.Thread(
            target=wheel.run_full_adaptation, 
            args=(st.session_state.latest_stats,)
        )
        thread.start()

# 4. If running, enter a lightweight UI refresh loop
if st.session_state.wheel_running:
    
    chart_placeholder = st.empty()
    metric_placeholder = st.empty()
    
    while thread.is_alive():
        # Update metrics, progress bars, and st.line_chart in the placeholder
        chart_placeholder.line_chart(st.session_state.latest_stats)
        time.sleep(0.5) # Prevent CPU thrashing on the web-server thread
