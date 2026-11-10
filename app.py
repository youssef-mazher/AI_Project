# ============================================================
# app.py — APPLICATION ENTRY POINT
# Put the Streamlit interface and main execution flow here.
# This file connects the other modules; keep algorithm logic
# in algorithms.py and data conversion in data_loader.py.
# ============================================================

# TODO: Import Streamlit.
# TODO: Import the functions/classes you need from:
#       models.py, data_loader.py, algorithms.py, evaluation.py

# TODO: Build the Streamlit page:
# 1. Page title and sidebar.
# 2. Input editors for rooms, lecturers, and courses.
# 3. Button to start optimization.
# 4. Call the data-loader functions.
# 5. Call the optimization pipeline.
# 6. Display the final timetable and comparison results.

import streamlit as st

from data_loader import (
    parse_rooms_from_gui,
    parse_lecturers_from_gui,
    parse_courses_from_gui,
    generate_all_timeslots
)

from algorithms import run_full_optimization_pipeline

from evaluation import *

if __name__ == "__main__":
    # TODO: Call your main Streamlit application function.
    pass
