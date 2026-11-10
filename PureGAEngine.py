import random, time
import GlobalConfiguration, FitnessEngine, DataModels



def find_lecturer_by_name(lecturers_list, lecturer_name):
    for lec in lecturers_list:
        if getattr(lec, 'name', None) == lecturer_name or (isinstance(lec, dict) and lec.get('name') == lecturer_name):
            return lec
        
    return lecturers_list[0] if lecturers_list else None



def create_random_individual(courses_list, rooms_list, lecturers_list, timeslots_list):
    individual_sessions = []

    doctors_list = []
    for l in lecturers_list:
        if l.get('type') == "Doctor":
            doctors_list.append(l)

    tas_list = []
    for l in lecturers_list:
        if l.get('type') == "TA":
            tas_list.append(l)

    lecture_halls = []
    for r in rooms_list:
        if r.get('type') == "Lecture Hall":
            lecture_halls.append(r)

    all_rooms = rooms_list

    for course in courses_list:
        if lecture_halls:
            lecture_room = random.choice(lecture_halls)
        else:
            lecture_room = all_rooms

        lecture_timeslot = random.choice(timeslots_list)
        doc_name = course.get('lecturer')
        assigned_doctor = find_lecturer_by_name(doctors_list, doc_name)
        lecture_session = DataModels.ScheduleSession(
            course = course,
            session_type = "Lecture",
            room = lecture_room,
            lecturer = assigned_doctor,
            timeslot = lecture_timeslot
        )

        individual_sessions.append(lecture_session)

        section_room = random.choice(all_rooms)
        section_timeslot = random.choice(timeslots_list)

        if len(tas_list) > 0:
            assigned_ta = random.choice(tas_list)
        else:
            assigned_ta = None

        section_session = DataModels.ScheduleSession(
            course = course,
            session_type = "Section",
            room = section_room,
            lecturer = assigned_ta,
            timeslot = section_timeslot
        )

        individual_sessions.append(section_session)

    return individual_sessions



def initialize_population(courses_list, rooms_list, lecturers_list, timeslots_list):
    population = []
    for i in range(GlobalConfiguration.POPULATION_SIZE):
        ind = create_random_individual(courses_list, rooms_list, lecturers_list, timeslots_list)
        population.append(ind)

    return population



def tournament_selection(scored_population):
    best_competitor = None
    best_score = -1

    for i in range(GlobalConfiguration.TOURNAMENT_SIZE):
        competitor = random.choice(scored_population)
        if competitor['fitness'] > best_score:
            best_score = competitor['fitness']
            best_competitor = competitor['individual']

    return best_competitor



def crossover(parent1, parent2):
    if len(parent1) <= 1:
        return parent1.copy(), parent2.copy()
    
    point = random.randint(1, len(parent1)-1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]

    return child1, child2



def mutate(individual, rooms_list, timeslots_list):
    for session in individual:
        if random.random() < GlobalConfiguration.MUTATION_RATE:
            if random.random() < 0.5:
                session.room = random.choice(rooms_list)
            else:
                session.timeslot = random.choice(timeslots_list)



def get_best_individual(scored_population):
    best_ind = scored_population[0]["individual"]
    max_fit = scored_population[0]["fitness"]

    for item in scored_population:
        if item["fitness"] > max_fit:
            max_fit = item["fitness"]
            best_ind = item["individual"]

    return best_ind



def run_pure_ga(courses_list, rooms_list, lecturers_list, timeslots_list):
    start_time = time.time()
    ga_fitness_history = []
    current_population = initialize_population(courses_list, rooms_list, lecturers_list, timeslots_list)
    best_ever_individual = None
    best_ever_fitness = -1

    for generation in range(1, GlobalConfiguration.MAX_GENERATIONS + 1):
        scored_population = []
        generation_best_fit = 0
        best_conflicts_in_gen = 0

        for ind in current_population:
            fit, conf, sof = FitnessEngine.calculate_fitness(ind)
            scored_population.append({
                "individual": ind,
                "fitness": fit,
                "conflicts": conf,
                "soft": sof
            })

            if fit > generation_best_fit:
                generation_best_fit = fit
                best_conflicts_in_gen = conf
            
            if fit > best_ever_fitness:
                best_ever_fitness = fit
                best_ever_individual = ind
    
        ga_fitness_history.append(generation_best_fit)

        if generation_best_fit >= 1.0 and best_conflicts_in_gen == 0:
            break

        next_population = []
        while len(next_population) < GlobalConfiguration.POPULATION_SIZE:
            p1 = tournament_selection(scored_population)
            p2 = tournament_selection(scored_population)
            c1, c2 = crossover(p1, p2)
            mutate(c1, rooms_list, timeslots_list)
            mutate(c2, rooms_list, timeslots_list)
            next_population.extend([c1, c2])
    
        current_population = next_population[:GlobalConfiguration.POPULATION_SIZE]
    
    end_time = time.time()
    exec_time = end_time - start_time

    return best_ever_individual, ga_fitness_history, exec_time
