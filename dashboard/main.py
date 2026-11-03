
# Define professional sidebar names without renaming our Python files
import streamlit as st

pages = [
    st.Page("app.py", title="Executive Overview", default=True),
    st.Page("pages/1_Decision_Simulator.py", title="Decision Simulator"),
    st.Page("pages/2_Mix_Comparison.py", title="Mix Comparison"),
    st.Page("pages/3_Strength_Analysis.py", title="Strength Analysis"),
]

# Display the navigation and run the selected page
pg = st.navigation(pages)
pg.run()
