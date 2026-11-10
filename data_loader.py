# ============================================================
# data_loader.py — INPUT PARSING / DATA PREPARATION
# Put the DataLoaderGUI module here.
# Convert Streamlit editor rows into model objects from models.py.
# ============================================================

# TODO: Import the required models from models.py.

# TODO: Add parse_string_to_list(text_input).
# TODO: Add parse_rooms_from_gui(rooms_df).
# TODO: Add parse_lecturers_from_gui(lecturers_df).
# TODO: Add parse_courses_from_gui(courses_df).
# TODO: Add generate_all_timeslots().

from models import (
    Course,
    Room,
    Lecturer,
    TimeSlot
)