import random
import time
import FitnessEngine
import DataModels
import GlobalConfiguration
# Check session conflicts

def session_has_conflicts(session, schedule):
    for other_session in schedule:
        # Skip the same object
        if other_session is session:
            continue
        same_day = (other_session.timeslot.day == session.timeslot.day)
        same_time = (other_session.timeslot.time_range == session.timeslot.time_range)
        if not (same_day and same_time):
            continue
        same_room = (other_session.room.name == session.room.name)
        same_lecturer = (other_session.lecturer.name == session.lecturer.name)
        common_group = (FitnessEngine.has_common_student_group(other_session.course,session.course))
        if same_room or same_lecturer or common_group:
            return True
    return False

# copy schedule
def deep_copy_schedule(schedule):
    cloned = []
    for s in schedule:
        cloned_session = DataModels.ScheduleSession(s.course,session_type=getattr(s, 'session_type', 'Lecture'), 
            room=s.room,lecturer=s.lecture,timeslot=s.timeslot)
        cloned.append(cloned_session)
    return cloned

# Fitness comparison
def get_score(schedule):
    fit, conflicts, soft = FitnessEngine.calculate_fitenss(schedule)
    return conflicts, soft

# Local search
def apply_memetic_local_search(individual_schedule, rooms_list, timeslots_list, max_passes=10):
    refined_schedule = deep_copy_schedule(individual_schedule)
    current_score = FitnessEngine.calculate_fitness(refined_schedule)[0]
    # current_score= get_score(refined_schedule)
    improved = False
    for _ in range(max_passes):
        improved = False
        for i in range(len(refined_schedule)):
            session = refined_schedule[i]
            # save original assignments
            original_slot = session.timeslot
            original_room = session.room
            best_slot = original_slot
            best_room = original_room
            best_score = current_score
            # try alternative timeslots
            for alt_slot in timeslots_list:
                if alt_slot == original_slot:
                    continue
                session.timeslot = alt_slot
                candidate_score = FitnessEngine.calculate_fitness(refined_schedule)[0]
                # candidate_score = get_score(refined_schedule)
                if candidate_score > best_score:
                    best_score = candidate_score
                    best_slot = alt_slot
                    best_room = original_room
                # restore original assignment
                session.timeslot = original_slot
                # session.room = original_room
            for alt_room in rooms_list:
                if alt_room == original_room:
                    continue
                session.room = alt_room
                candidate_score = FitnessEngine.calculate_fitness(refined_schedule)[0]
                if candidate_score > best_score:
                    best_score = candidate_score
                    best_slot = original_slot
                    best_room = alt_room
                session.room = original_room
                
            # accept best imporvement
            if best_score > current_score:
                session.timeslot = best_slot
                session.room = best_room
                current_score = best_score
                improved = True
            if not improved:
                break
    return refined_schedule
                
# run memetic function
def run_memetic_algorithm(courses_list, rooms_list, lecturers_list, timeslots_list):
    start_time = time.time()
    
    from PureGAEngine import initialize_population, tournament_selection, crossover, mutate

    current_population = initialize_population(courses_list, rooms_list, lecturers_list, timeslots_list)
    best_ever_individual = None
    best_ever_fitness = -1
    fitness_history = []

    generations = getattr(GlobalConfiguration, 'MAX_GENERATIONS', 10)
    pop_size = getattr(GlobalConfiguration, 'POPULATION_SIZE', 6)

    for generation in range(1, generations + 1):
        scored_population = []
        gen_best_fit = 0
        gen_conflicts = 0

        for ind in current_population:
            fit, conf, sof = get_score(ind)
            scored_population.append({
                "individual": ind,
                "fitness": fit,
                "conflicts": conf,
                "soft": sof
            })

            if fit > gen_best_fit:
                gen_best_fit = fit
                gen_conflicts = conf
            
            if fit > best_ever_fitness:
                best_ever_fitness = fit
                best_ever_individual = ind

        fitness_history.append(gen_best_fit)
        print(f"Generation {generation} | Best Fitness: {gen_best_fit:.4f} | Conflicts: {gen_conflicts}")

        if gen_best_fit >= 1.0 and gen_conflicts == 0:
            print("Optimal solution found!")
            break

        next_population = []
        while len(next_population) < pop_size:
            p1 = tournament_selection(scored_population)
            p2 = tournament_selection(scored_population)
            c1, c2 = crossover(p1, p2)
            
            mutate(c1, rooms_list, timeslots_list)
            mutate(c2, rooms_list, timeslots_list)

            if random.random() < 0.3: 
                c1 = apply_memetic_local_search(c1, rooms_list, timeslots_list, max_passes=2)
            if random.random() < 0.3:
                c2 = apply_memetic_local_search(c2, rooms_list, timeslots_list, max_passes=2)

            next_population.extend([c1, c2])

        current_population = next_population[:pop_size]

    exec_time = time.time() - start_time
    return best_ever_individual, fitness_history, exec_time
