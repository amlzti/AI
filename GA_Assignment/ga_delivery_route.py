"""
GA Assignment — Genetic Algorithm for Delivery Route Optimisation

A delivery van starts at depot A, visits B, C, D, E, F and G exactly once,
and returns to A. The GA searches for the visiting order with the shortest
total distance (km).

Run: python ga_delivery_route.py
"""

import numpy as np

# ---------------------------------------------------------------------
# 1. Dataset: symmetric distance matrix (km)
# ---------------------------------------------------------------------
LOCATIONS = ["A", "B", "C", "D", "E", "F", "G"]
DEPOT = 0  # index of A

DISTANCE_KM = np.array([
    #  A  B  C  D  E  F  G
    [0, 4, 8, 6, 7, 9, 5],  # A
    [4, 0, 5, 7, 3, 8, 6],  # B
    [8, 5, 0, 4, 6, 3, 7],  # C
    [6, 7, 4, 0, 5, 6, 8],  # D
    [7, 3, 6, 5, 0, 4, 6],  # E
    [9, 8, 3, 6, 4, 0, 5],  # F
    [5, 6, 7, 8, 6, 5, 0],  # G
])

DELIVERY_STOPS = np.arange(1, len(LOCATIONS))  # B..G as indices 1..6

# ---------------------------------------------------------------------
# 2. GA settings (fixed seed for reproducibility)
# ---------------------------------------------------------------------
SEED = 42
POP_SIZE = 50
GENERATIONS = 100
TOURNAMENT_SIZE = 3
MUTATION_RATE = 0.2
N_ELITE = 2


def route_distance(chromosome):
    """Total distance: A -> stops in chromosome order -> back to A."""
    full_route = np.r_[DEPOT, chromosome, DEPOT]
    return int(DISTANCE_KM[full_route[:-1], full_route[1:]].sum())


def route_to_text(chromosome):
    return " -> ".join(LOCATIONS[i] for i in np.r_[DEPOT, chromosome, DEPOT])


def initial_population(rng):
    """Each chromosome is a random permutation of B..G (always valid)."""
    return [rng.permutation(DELIVERY_STOPS) for _ in range(POP_SIZE)]


def tournament_selection(population, distances, rng):
    """Pick TOURNAMENT_SIZE random routes; the shortest one becomes a parent."""
    contestants = rng.choice(len(population), TOURNAMENT_SIZE, replace=False)
    winner = contestants[np.argmin(distances[contestants])]
    return population[winner]


def order_crossover(parent_a, parent_b, rng):
    """Order crossover (OX): copy a slice from parent A, then fill the
    remaining positions with parent B's stops in B's order, skipping any
    stop already used. The child never repeats or misses a location."""
    size = len(parent_a)
    start, end = sorted(rng.choice(size, 2, replace=False))
    child = np.full(size, -1)
    child[start:end + 1] = parent_a[start:end + 1]

    remaining = [stop for stop in parent_b if stop not in child]
    empty_positions = [i for i in range(size) if child[i] == -1]
    child[empty_positions] = remaining
    return child


def swap_mutation(chromosome, rng):
    """With probability MUTATION_RATE, swap two stops. Still a valid route."""
    child = chromosome.copy()
    if rng.random() < MUTATION_RATE:
        i, j = rng.choice(len(child), 2, replace=False)
        child[i], child[j] = child[j], child[i]
    return child


def run_ga(seed=SEED):
    rng = np.random.default_rng(seed)
    population = initial_population(rng)

    best_route, best_distance = None, np.inf
    history = []

    for generation in range(1, GENERATIONS + 1):
        # Fitness: total route distance (lower is better).
        distances = np.array([route_distance(r) for r in population])

        # Track the best-so-far route.
        if distances.min() < best_distance:
            best_distance = distances.min()
            best_route = population[distances.argmin()].copy()
        history.append(best_distance)

        if generation in (1, 10, 25, 50, GENERATIONS):
            print(f"Generation {generation:3d}: best distance = {best_distance} km")

        # Elitism: copy the shortest routes unchanged.
        elite_idx = np.argsort(distances)[:N_ELITE]
        next_population = [population[i].copy() for i in elite_idx]

        # Fill the rest with selection -> crossover -> mutation.
        while len(next_population) < POP_SIZE:
            parent_a = tournament_selection(population, distances, rng)
            parent_b = tournament_selection(population, distances, rng)
            child = order_crossover(parent_a, parent_b, rng)
            child = swap_mutation(child, rng)
            next_population.append(child)

        population = next_population

    return best_route, best_distance, history


def main():
    print("=" * 60)
    print("GA ASSIGNMENT — DELIVERY ROUTE OPTIMISATION")
    print("=" * 60)
    print(f"Seed: {SEED} | Population: {POP_SIZE} | Generations: {GENERATIONS}")
    print(f"Tournament size: {TOURNAMENT_SIZE} | Mutation rate: {MUTATION_RATE} "
          f"| Elites: {N_ELITE}\n")

    best_route, best_distance, _ = run_ga()

    print("\nBEST ROUTE FOUND")
    print("Route:", route_to_text(best_route))
    print(f"Total distance: {best_distance} km")


if __name__ == "__main__":
    main()
