import streamlit as st
import os
import json
from controllers.matches_controller import (
    handle_add_match,
    handle_view_matches
)

# Get project root directory (parent of views)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Path to the JSON file (correct filename)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "TEAMS_BY_LEAGUE.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    TEAMS_BY_LEAGUE = json.load(f)

def matches_view():
    st.title("🏟️ Add & View Matches")

    tab1, tab2 = st.tabs(["➕ Add Match", "📋 View Matches"])

    with tab1:
        handle_add_match(TEAMS_BY_LEAGUE)

    with tab2:
        handle_view_matches()
