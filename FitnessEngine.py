from collections import defaultdict
from functools import lru_cache

import GlobalConfiguration

LECTURE = "lecture"
SECTION = "section"
DOCTOR = "doctor"
TA = "ta"

# عشان نهندل الداتا اللي جيالي من باقي الموديولز
def to_int(value, default=0):
    try:
        return int(float(value))    # عشان لو الداتا فيها "3.0" أو "3.5" نقدر نحولها لـ int منغير ما نرمي ValueError
    except (TypeError, ValueError):
        return default

def normalize_session_type(value):
    text = str(value or "").strip().lower()
    if text in ("section", "sec", "lab", "سكشن"):
        return SECTION
    return LECTURE

def get_role(lecturer):
    role = str(getattr(lecturer, "role", "") or "").strip().lower()
    if role in ("doctor", "dr", "prof", "professor", "دكتور"):
        return DOCTOR
    if role in ("ta", "teaching assistant", "assistant", "معيد"):
        return TA
    return None

def is_lab_room(room):
    return "lab" in str(getattr(room, "type", "")).lower()

@lru_cache(maxsize=None)
def parse_time_range(time_range):
    start_str, end_str = time_range.split("-")
    start, end = int(start_str), int(end_str)
    if start < 8:          
        start += 12
    if end <= start:       
        end += 12
    return start, end

def has_common_student_group(course_A, course_B):
    common_levels = set(course_A.levels) & set(course_B.levels)
    common_depts = set(course_A.departments) & set(course_B.departments)
    return bool(common_levels) and bool(common_depts)

# hard constraints for a single session
def room_type_ok(session_or_course_type, room):
    stype = normalize_session_type(session_or_course_type)
    return is_lab_room(room) if stype == SECTION else not is_lab_room(room)

def capacity_ok(room, course):
    students = to_int(getattr(course, "students_count", 0))
    if students <= 0:                       
        return True
    return to_int(getattr(room, "capacity", 0)) >= students

def lecturer_role_ok(course, lecturer):
    role = get_role(lecturer)
    if role is None:
        return True
    stype = normalize_session_type(getattr(course, "session_type", None))
    return role == (TA if stype == SECTION else DOCTOR)

def session_violations(session):
    course = session.course
    return {
        "room_type": 0 if room_type_ok(getattr(course, "session_type", None), session.room) else 1,
        "lecturer_role": 0 if lecturer_role_ok(course, session.lecturer) else 1,
        "capacity": 0 if capacity_ok(session.room, course) else 1,
    }

# hard constraints 
def group_by_slot(schedule_list):
    buckets = defaultdict(list)
    for s in schedule_list:
        buckets[(s.timeslot.day, s.timeslot.time_range)].append(s)
    return buckets

def count_hard_conflicts(schedule_list):
    details = {
        "room": 0, "lecturer": 0, "student_group": 0,       
        "room_type": 0, "lecturer_role": 0, "capacity": 0,  
    }

    for sessions in group_by_slot(schedule_list).values():
        for i in range(len(sessions)):
            for j in range(i + 1, len(sessions)):
                a, b = sessions[i], sessions[j]
                if a.room.name == b.room.name:
                    details["room"] += 1
                if a.lecturer.name == b.lecturer.name:
                    details["lecturer"] += 1
                if has_common_student_group(a.course, b.course):
                    details["student_group"] += 1

    for s in schedule_list:
        for key, value in session_violations(s).items():
            details[key] += value

    return details

# soft constraintshr
def count_lecturer_overload(schedule_list):   #per day
    hours = defaultdict(int)
    limits = {}
    for s in schedule_list:
        start, end = parse_time_range(s.timeslot.time_range)
        key = (s.lecturer.name, s.timeslot.day)
        hours[key] += end - start
        limits[key] = to_int(getattr(s.lecturer, "max_hours_per_day", 24), 24)
    return sum(max(0, h - limits[k]) for k, h in hours.items())

def ta_weekly_hours(schedule_list):    #per week
    hours = defaultdict(int)
    for s in schedule_list:
        if get_role(s.lecturer) == TA:
            start, end = parse_time_range(s.timeslot.time_range)
            hours[s.lecturer.name] += end - start
    return dict(hours)

def count_ta_imbalance(schedule_list):
    daily = defaultdict(lambda: defaultdict(int))     # {ta: {day: hours}}
    for s in schedule_list:
        if get_role(s.lecturer) == TA:
            start, end = parse_time_range(s.timeslot.time_range)
            daily[s.lecturer.name][s.timeslot.day] += end - start

    if len(daily) < 2:        
        return 0

    total = 0
    for day in GlobalConfiguration.ALLOWED_DAYS:
        loads = [daily[ta].get(day, 0) for ta in daily]
        total += max(loads) - min(loads)
    return total

def count_student_gaps(schedule_list):    #بيعد في كام جاب مش بيقول هما ساعه ولا اتنين 
    gaps = 0
    levels = getattr(GlobalConfiguration, "LEVELS", [1, 2, 3, 4])
    for day in GlobalConfiguration.ALLOWED_DAYS:
        for level in levels:
            day_sessions = [
                s for s in schedule_list
                if level in s.course.levels and s.timeslot.day == day
            ]
            if len(day_sessions) > 1:
                day_sessions.sort(key=lambda s: parse_time_range(s.timeslot.time_range)[0])
                for cur, nxt in zip(day_sessions, day_sessions[1:]):
                    if parse_time_range(nxt.timeslot.time_range)[0] > \
                       parse_time_range(cur.timeslot.time_range)[1]:
                        gaps += 1
    return gaps

def calculate_soft_violations(schedule_list):
    return (count_student_gaps(schedule_list)
            + count_lecturer_overload(schedule_list)
            + count_ta_imbalance(schedule_list))

# كل الهري اللي فوق ده عشان نعمل الفانكشن دي
def calculate_fitness(schedule_list):
    if not schedule_list:
        return 0.0, 0, 0

    hard_conflicts = sum(count_hard_conflicts(schedule_list).values())
    soft_violations = calculate_soft_violations(schedule_list)

    total_penalty = (hard_conflicts * GlobalConfiguration.HARD_PENALTY_WEIGHT
                     + soft_violations * GlobalConfiguration.SOFT_PENALTY_WEIGHT)
    fitness_value = 1.0 / (1.0 + total_penalty)
    return fitness_value, hard_conflicts, soft_violations

def get_conflict_details(schedule_list):
    details = count_hard_conflicts(schedule_list)
    details["student_gaps"] = count_student_gaps(schedule_list)
    details["lecturer_overload_hours"] = count_lecturer_overload(schedule_list)
    details["ta_daily_imbalance_hours"] = count_ta_imbalance(schedule_list)
    return details

