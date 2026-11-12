import random
import time
import PureGAEngine
import MemeticRefinementLayer
import FitnessEngine


def to_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def validate_inputs(courses_list, rooms_list, lecturers_list):
    if not courses_list or not rooms_list or not lecturers_list:
        raise ValueError("courses, rooms and lecturers must all be non-empty.")

    warnings = []
    lecturers_by_name = {lec.name: lec for lec in lecturers_list}

    for course in courses_list:
        stype = FitnessEngine.normalize_session_type(getattr(course, "session_type", None))
        lec = lecturers_by_name.get(course.assigned_lecturer)

        if lec is None:
            warnings.append(f"Course '{course.name}' has unknown lecturer '{course.assigned_lecturer}'")
        elif not FitnessEngine.lecturer_role_ok(course, lec):
            needed = "a Teaching Assistant" if stype == FitnessEngine.SECTION else "a Doctor"
            warnings.append(f"'{course.name}' is a {stype} and needs {needed}, "
                            f"but '{lec.name}' has role '{getattr(lec, 'role', '?')}'")

        if not any(FitnessEngine.room_fits_course(r, course) for r in rooms_list):
            warnings.append(f"No room fits '{course.name}' (needs "
                            f"{'Lab' if stype == FitnessEngine.SECTION else 'Lecture Hall'}, "
                            f"students={getattr(course, 'students_count', '?')})")

    ta_hours = {}
    for course in courses_list:
        lec = lecturers_by_name.get(course.assigned_lecturer)
        if lec is not None and FitnessEngine.get_role(lec) == FitnessEngine.TA:
            ta_hours[lec.name] = ta_hours.get(lec.name, 0) + to_int(course.weekly_hours) * 2

    if len(ta_hours) >= 2:
        busiest = max(ta_hours, key=ta_hours.get)
        lightest = min(ta_hours, key=ta_hours.get)
        if ta_hours[busiest] - ta_hours[lightest] > 4:
            warnings.append(f"TA workload is unbalanced: '{busiest}' has {ta_hours[busiest]}h/week "
                            f"vs '{lightest}' {ta_hours[lightest]}h/week. "
                            f"Consider reassigning courses (the GA cannot change this).")
    return warnings


def build_package(individual, history):
    fit, conf, soft = FitnessEngine.calculate_fitness(individual)
    return {
        "Individual": individual,
        "History": history,
        "FinalFitness": fit,
        "FinalConflicts": conf,
        "FinalSoftViolations": soft,
        "ConflictDetails": FitnessEngine.get_conflict_details(individual),
        "TAWeeklyHours": FitnessEngine.ta_weekly_hours(individual),
    }


def run_full_optimization_pipeline(courses_list, rooms_list, lecturers_list,
                                   timeslots_list, seed=None):
    warnings = validate_inputs(courses_list, rooms_list, lecturers_list)
    if seed is not None:
        random.seed(seed)

    #  تشغيل الـ GA القياسي
    ga_best_ind, ga_history, ga_exec_time = PureGAEngine.run_pure_ga(
        courses_list, rooms_list, lecturers_list, timeslots_list
    )
    GA_Results_Package = build_package(ga_best_ind, ga_history)
    GA_Results_Package["ExecutionTime"] = ga_exec_time

    #  تطبيق طبقة البحث المحلي (MA)
    t0 = time.perf_counter()
    ma_best_ind = MemeticRefinementLayer.apply_memetic_local_search(
        ga_best_ind, rooms_list, timeslots_list
    )
    refinement_time = time.perf_counter() - t0

    Refined_Results_Package = build_package(ma_best_ind, None)
    Refined_Results_Package["History"] = list(ga_history) + [Refined_Results_Package["FinalFitness"]]
    Refined_Results_Package["TotalExecutionTime"] = ga_exec_time + refinement_time
    Refined_Results_Package["RefinementTime"] = refinement_time
    #المقارنه بقا
    Refined_Results_Package["Comparison"] = {
        "conflicts_removed": GA_Results_Package["FinalConflicts"] - Refined_Results_Package["FinalConflicts"],
        "soft_reduced": GA_Results_Package["FinalSoftViolations"] - Refined_Results_Package["FinalSoftViolations"],
        "fitness_gain": Refined_Results_Package["FinalFitness"] - GA_Results_Package["FinalFitness"],
    }
    Refined_Results_Package["Warnings"] = warnings

    return GA_Results_Package, Refined_Results_Package