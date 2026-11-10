# ============================================================
# algorithms.py — ALL OPTIMIZATION LOGIC
# Put these four modules/sections in this one file, in this order:
#
# 1. FitnessEngine
#    - has_common_student_group()
#    - calculate_soft_violations()
#    - calculate_fitness()
#
# 2. PureGAEngine
#    - find_lecturer_by_name()
#    - create_random_individual()
#    - initialize_population()
#    - tournament_selection()
#    - crossover()
#    - mutate()
#    - get_best_individual()
#    - run_pure_ga()
#
# 3. MemeticRefinementLayer
#    - session_has_conflict()
#    - deep_copy_schedule()
#    - apply_memetic_local_search()
#
# 4. MemeticPipelineAndComparison
#    - run_full_optimization_pipeline()
#
# Keep the order above so the functions are defined before they
# are used. Import models/configuration from models.py.
# ============================================================

# TODO: Import random/time utilities and required classes/constants
#       from models.py.

# -------------------- 1. FITNESS ENGINE --------------------
# TODO: Add FitnessEngine functions here.

# -------------------- 2. PURE GENETIC ALGORITHM (GA) --------------------
# TODO: Add PureGAEngine functions here.

# -------------------- 3. MEMETIC LOCAL SEARCH (MA) --------------------
# TODO: Add MemeticRefinementLayer functions here.

# -------------------- 4. OPTIMIZATION PIPELINE --------------------
# TODO: Add run_full_optimization_pipeline() here.

from models import (
    Course,
    Room,
    Lecturer,
    TimeSlot,
    ScheduleSession,
    POPULATION_SIZE,
    MAX_GENERATIONS,
    MUTATION_RATE,
    TOURNAMENT_SIZE,
    HARD_PENALTY_WEIGHT,
    SOFT_PENALTY_WEIGHT,
    ALLOWED_DAYS,
    ALLOWED_TIMES
)