import pandas as pd
import DataModels , GlobalConfiguration  

# Convert the text entered by the user into a list
def parse_string_to_list(text_input):

    if text_input is None:
        return []

    if isinstance(text_input, list): # It checks the data type
        return text_input

    if pd.isna(text_input) or str(text_input).strip() == "":
        return []

    return [item.strip()
        for item in str(text_input).split(",")
        if item.strip()]

# Converting room and laboratory data from a GUI table into Room Objects
def parse_rooms_from_gui(rooms_df):

    rooms_list = []
    for _, row in rooms_df.iterrows():
        if pd.notna(row["Room Name"]) and str(row["Room Name"]).strip():
            room_obj = DataModels.Room(
                name = row["Room Name"],
                capacity = int(row["Capacity"]),
                room_type = row["Type"])
            rooms_list.append(room_obj)
    return rooms_list

# Converting data for professors and teaching assistants into Lecturer objects
def parse_lecturers_from_gui(lecturers_df):

    lecturers_list = []
    for _, row in lecturers_df.iterrows():
        if pd.notna(row["Name"]) and str(row["Name"]).strip():
            lecturer_obj = DataModels.Lecturer(
                name = row["Name"],
                lecturer_type = row["Type"],
                max_hours_per_day = int(row["Max Hours/Day"]))
            lecturers_list.append(lecturer_obj)
    return lecturers_list

# Converting the course schedule into Course Objects
def parse_courses_from_gui(courses_df):
    courses_list = []
    for index, row in courses_df.iterrows():
        if pd.notna(row["Course Name"]) and str(row["Course Name"]).strip():
            course_obj = DataModels.Course(
                id = index + 1,
                name = row["Course Name"],
                levels = parse_string_to_list(row["Level"]),
                departments = parse_string_to_list(row["Dept"]),
                weekly_hours = row.get("Weekly Hours", 1),
                assigned_lecturer = parse_string_to_list(row["Lecturers"]))
            courses_list.append(course_obj)
    return courses_list


def load_all_data(rooms_df, lecturers_df, courses_df):

    rooms = parse_rooms_from_gui(rooms_df)
    lecturers = parse_lecturers_from_gui(lecturers_df)
    courses = parse_courses_from_gui(courses_df)
    return {"rooms": rooms,"lecturers": lecturers,"courses": courses}

