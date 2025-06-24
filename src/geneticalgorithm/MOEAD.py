import numpy as np
from src.geneticalgorithm.NDTree import NDTree
from src.geneticalgorithm.Individual import Individual

class MOEAD:
    def __init__(self, population_size, number_of_objectives, neighborhood_size):
        self.population_size = population_size
        self.number_of_objectives = number_of_objectives
        self.neighborhood_size = neighborhood_size
        self.weight_vectors = []
        self.neighborhoods = []
        self.reference_point = np.zeros(self.number_of_objectives)
        self.population = None
        self.nd_tree = NDTree(maximum_size=20, minimum_children_size=6)  # ND-Tree for efficient dominance checks
        
    def _generate_combinations(self, m, H):
        """Generate all combinations of m non-negative integers that sum to H."""
        if m == 1:
            return [[H]]
        
        combinations = []
        for i in range(H + 1):
            sub_combinations = self._generate_combinations(m - 1, H - i)
            for sub in sub_combinations:
                combinations.append([i] + sub)
        return combinations

    def initialize_weight_vectors(self):
        
        m = self.number_of_objectives
        H = 12
        while True:
            n_vectors = len(self._generate_combinations(m, H))
            if n_vectors >= self.population_size:
                break
            H += 1
        
        # Generate all combinations
        combinations = self._generate_combinations(m, H)
        
        # Convert combinations to weight vectors
        for combo in combinations:
            w = np.array(combo) / H
            self.weight_vectors.append(w)
        
        # If we generated more vectors than needed, randomly select population_size of them
        if len(self.weight_vectors) > self.population_size:
            np.random.shuffle(self.weight_vectors)
            self.weight_vectors = self.weight_vectors[:self.population_size]
            
    def initialize_neighborhoods(self):
        # Calculate Euclidean distances between weight vectors
        distances = np.zeros((self.population_size, self.population_size))
        for i in range(self.population_size):
            for j in range(self.population_size):
                distances[i][j] = np.linalg.norm(self.weight_vectors[i] - self.weight_vectors[j])
                
        # Sort distances and get neighborhoods
        for i in range(self.population_size):
            sorted_indices = np.argsort(distances[i])
            # Convert numpy array to list and store neighborhood indices
            self.neighborhoods.append(sorted_indices[1:self.neighborhood_size + 1].tolist())
            
    def initialize_reference_point(self, population):
        for i in range(self.number_of_objectives):
            self.reference_point[i] = min(ind.aptitudes[i] for ind in population.initial_population)

    def update_reference_point(self, offspring: Individual):
        # Update reference point based on the new offspring
        for i in range(self.number_of_objectives):
            self.reference_point[i] = min(self.reference_point[i], offspring.aptitudes[i])
                
    def tchebycheff_scalarization(self, individual, weight_vector):
        # Calculate Tchebycheff scalarization
        max_value = -np.inf
        for i in range(self.number_of_objectives):
            value = weight_vector[i] * abs(individual.aptitudes[i] - self.reference_point[i])
            if value > max_value:
                max_value = value
        return max_value

    def dominates(self, individual1, individual2):
        """Check if individual1 dominates individual2"""

        # Check if individual1 is better or equal in every objective
        for i in range(self.number_of_objectives):
            isBetterOrEqual = individual1.aptitudes[i] <= individual2.aptitudes[i]
            if not isBetterOrEqual:
                return False

        #Check if individual1 is better at least in one objective
        for i in range(self.number_of_objectives):
            isBetter = individual1.aptitudes[i] < individual2.aptitudes[i]
            if isBetter:
                return True
        return False
    
    @property
    def external_population(self):
        return self.nd_tree.get_solutions()
    
    def update_external_population(self, new_solution):
        """Update the external population with a new solution"""
        self.nd_tree.update(new_solution)


        # is_dominated = False
        # non_dominated_solutions = []
        
        # for sol in self.external_population:
        #     if self.dominates(sol, new_solution):
        #         is_dominated = True
        #         break
        #     if not self.dominates(new_solution, sol):
        #         non_dominated_solutions.append(sol)
        
        # # Only update if the new solution is not dominated
        # if not is_dominated:
        #     self.external_population = non_dominated_solutions + [new_solution]